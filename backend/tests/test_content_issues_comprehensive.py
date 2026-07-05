import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.models.content_issue import ContentIssue


def _signup(client: TestClient, email: str) -> dict:
    resp = client.post("/api/auth/signup", json={
        "email": f"issue_{email}@example.com",
        "password": "TestPass123!",
        "full_name": f"Issue User {email}",
    })
    return resp.json()


def _test_db():
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    return db, gen


@pytest.fixture(autouse=True)
def _mock_celery(monkeypatch):
    monkeypatch.setattr("app.routes.api.issues.review_content_issue.delay", MagicMock())


def test_create_issue_valid(client: TestClient):
    user = _signup(client, "create_valid")
    token = user["access_token"]
    resp = client.post("/api/issues", json={
        "content_type": "topic",
        "content_id": "topic_123",
        "section_index": 2,
        "severity": "medium",
        "description": "This explanation is confusing",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "open"
    assert "id" in data
    assert "AI is reviewing" in data["message"]


def test_create_issue_triggers_ai_review(client: TestClient, monkeypatch):
    triggered = {"called": False}

    def mock_delay(issue_id):
        triggered["called"] = True
        return None

    monkeypatch.setattr("app.routes.api.issues.review_content_issue.delay", mock_delay)

    user = _signup(client, "trig_ai")
    token = user["access_token"]
    client.post("/api/issues", json={
        "content_type": "topic",
        "content_id": "topic_456",
        "severity": "high",
        "description": "Contains errors",
    }, headers={"Authorization": f"Bearer {token}"})
    assert triggered["called"] is True


def test_create_issue_missing_content_type(client: TestClient):
    user = _signup(client, "miss_ct")
    token = user["access_token"]
    resp = client.post("/api/issues", json={
        "content_id": "topic_1",
        "severity": "low",
        "description": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


def test_create_issue_missing_content_id(client: TestClient):
    user = _signup(client, "miss_cid")
    token = user["access_token"]
    resp = client.post("/api/issues", json={
        "content_type": "topic",
        "severity": "low",
        "description": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


def test_create_issue_missing_severity(client: TestClient):
    user = _signup(client, "miss_sev")
    token = user["access_token"]
    resp = client.post("/api/issues", json={
        "content_type": "topic",
        "content_id": "topic_1",
        "description": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


def test_create_issue_missing_description(client: TestClient):
    user = _signup(client, "miss_desc")
    token = user["access_token"]
    resp = client.post("/api/issues", json={
        "content_type": "topic",
        "content_id": "topic_1",
        "severity": "low",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


def test_create_issue_invalid_severity(client: TestClient):
    user = _signup(client, "bad_sev")
    token = user["access_token"]
    resp = client.post("/api/issues", json={
        "content_type": "topic",
        "content_id": "topic_1",
        "severity": "extremely_critical",
        "description": "test",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201


def test_create_issue_without_section_index(client: TestClient):
    user = _signup(client, "no_sidx")
    token = user["access_token"]
    resp = client.post("/api/issues", json={
        "content_type": "topic",
        "content_id": "topic_1",
        "severity": "medium",
        "description": "General issue",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "open"


def test_list_issues_empty(client: TestClient):
    user = _signup(client, "list_empty")
    token = user["access_token"]
    resp = client.get("/api/issues", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["issues"] == []


def test_list_issues_with_issues(client: TestClient):
    user = _signup(client, "list_with")
    token = user["access_token"]
    client.post("/api/issues", json={
        "content_type": "topic", "content_id": "t1", "severity": "low", "description": "d1",
    }, headers={"Authorization": f"Bearer {token}"})
    client.post("/api/issues", json={
        "content_type": "section", "content_id": "t2", "severity": "high", "description": "d2", "section_index": 1,
    }, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/api/issues", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    issues = resp.json()["issues"]
    assert len(issues) >= 2


def test_list_issues_only_own_issues(client: TestClient):
    u1 = _signup(client, "own_u1")
    u2 = _signup(client, "own_u2")
    t1 = u1["access_token"]
    t2 = u2["access_token"]

    client.post("/api/issues", json={
        "content_type": "topic", "content_id": "t1", "severity": "low", "description": "u1 issue",
    }, headers={"Authorization": f"Bearer {t1}"})
    client.post("/api/issues", json={
        "content_type": "topic", "content_id": "t2", "severity": "high", "description": "u2 issue",
    }, headers={"Authorization": f"Bearer {t2}"})

    resp = client.get("/api/issues", headers={"Authorization": f"Bearer {t1}"})
    issues = resp.json()["issues"]
    assert all(i["description"] == "u1 issue" for i in issues)


def test_list_issues_pagination(client: TestClient):
    user = _signup(client, "list_pag")
    token = user["access_token"]
    for i in range(5):
        client.post("/api/issues", json={
            "content_type": "topic", "content_id": f"t{i}", "severity": "low", "description": f"d{i}",
        }, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/api/issues?skip=0&limit=2", headers={"Authorization": f"Bearer {token}"})
    assert len(resp.json()["issues"]) == 2


def test_create_issue_very_long_description(client: TestClient):
    user = _signup(client, "long_desc")
    token = user["access_token"]
    long_description = "A" * 10000
    resp = client.post("/api/issues", json={
        "content_type": "topic",
        "content_id": "topic_long",
        "severity": "low",
        "description": long_description,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201


def test_create_issue_sql_injection_attempt(client: TestClient):
    user = _signup(client, "sqli")
    token = user["access_token"]
    resp = client.post("/api/issues", json={
        "content_type": "topic",
        "content_id": "1; DROP TABLE users; --",
        "severity": "high",
        "description": "'; DELETE FROM content_issues; --",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "open"

    db, gen = _test_db()
    try:
        assert db.query(ContentIssue).count() >= 1
    finally:
        gen.close()


def test_create_issue_unauthenticated(client: TestClient):
    resp = client.post("/api/issues", json={
        "content_type": "topic", "content_id": "t1", "severity": "low", "description": "test",
    })
    assert resp.status_code in (401, 403)


def test_list_issues_unauthenticated(client: TestClient):
    resp = client.get("/api/issues")
    assert resp.status_code in (401, 403)
