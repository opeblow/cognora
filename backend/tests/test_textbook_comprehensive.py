import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.models.subject import Subject
from app.models.lesson import Lesson, Topic
from app.services.textbook_service import TEXTBOOK_SECTIONS


def _test_db():
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    return db, gen


@pytest.fixture
def seed_subject_topic():
    db, gen = _test_db()
    try:
        subj = Subject(name="Mathematics", slug="mathematics", description="Math", category="science")
        db.add(subj)
        db.flush()
        lesson = Lesson(subject_id=subj.id, title="Algebra Basics", slug="algebra-basics", order_index=1)
        db.add(lesson)
        db.flush()
        topic = Topic(lesson_id=lesson.id, title="Linear Equations", content="Intro", order_index=1)
        db.add(topic)
        db.commit()
        yield subj, topic
    finally:
        gen.close()


def _signup(client: TestClient, email: str) -> dict:
    resp = client.post("/api/auth/signup", json={
        "email": f"tb_{email}@example.com",
        "password": "TestPass123!",
        "full_name": f"TB User {email}",
    })
    return resp.json()


def test_get_plan_valid(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "plan_ok")
    token = user["access_token"]

    resp = client.get(
        f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/plan",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["topic_id"] == topic.id
    assert data["topic_title"] == "Linear Equations"
    assert data["subject_name"] == "Mathematics"
    assert data["total_sections"] == 10
    assert len(data["sections"]) == 10
    assert data["sections"][0]["title"] == "Learning Objectives & Introduction"


def test_get_plan_topic_not_found(client: TestClient, seed_subject_topic):
    subj, _ = seed_subject_topic
    user = _signup(client, "plan_nf")
    token = user["access_token"]
    resp = client.get(
        f"/api/subjects/{subj.slug}/topics/nonexistent/textbook/plan",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_get_plan_subject_not_found(client: TestClient, seed_subject_topic):
    _, topic = seed_subject_topic
    user = _signup(client, "plan_nosubj")
    token = user["access_token"]
    resp = client.get(
        f"/api/subjects/nonexistent/topics/{topic.id}/textbook/plan",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_get_plan_unauthenticated(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    resp = client.get(f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/plan")
    assert resp.status_code in (401, 403)


def test_get_status_valid(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "stat_ok")
    token = user["access_token"]

    with patch("app.routes.api.textbook.TextbookService.get_generated_sections", new_callable=AsyncMock) as mock:
        mock.return_value = [0, 1, 2]
        resp = client.get(
            f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/status",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sections"] == 10
    assert data["generated_sections"] == [0, 1, 2]
    secs = {s["index"]: s["has_content"] for s in data["sections"]}
    assert secs[0] is True
    assert secs[3] is False


def test_get_status_all_sections(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "stat_all")
    token = user["access_token"]

    with patch("app.routes.api.textbook.TextbookService.get_generated_sections", new_callable=AsyncMock) as mock:
        mock.return_value = list(range(10))
        resp = client.get(
            f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/status",
            headers={"Authorization": f"Bearer {token}"},
        )
    sections = resp.json()["sections"]
    assert all(s["has_content"] for s in sections)


def test_get_status_partial_sections(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "stat_part")
    token = user["access_token"]

    with patch("app.routes.api.textbook.TextbookService.get_generated_sections", new_callable=AsyncMock) as mock:
        mock.return_value = [0, 2, 4, 6, 8]
        resp = client.get(
            f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/status",
            headers={"Authorization": f"Bearer {token}"},
        )
    sections = resp.json()["sections"]
    assert sections[0]["has_content"] is True
    assert sections[1]["has_content"] is False
    assert sections[2]["has_content"] is True


def test_get_section_valid(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "sec_ok")
    token = user["access_token"]

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock:
        mock.return_value = "<h3>Test Content</h3>"
        resp = client.get(
            f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/0",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["index"] == 0
    assert data["title"] == TEXTBOOK_SECTIONS[0]["title"]
    assert data["content"] == "<h3>Test Content</h3>"
    assert data["has_content"] is True


def test_get_section_out_of_range(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "sec_oob")
    token = user["access_token"]
    resp = client.get(
        f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/99",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_get_section_negative_index(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "sec_neg")
    token = user["access_token"]
    resp = client.get(
        f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/-1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404


def test_get_section_not_cached(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "sec_nocache")
    token = user["access_token"]

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock:
        mock.return_value = None
        resp = client.get(
            f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/0",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["content"] == ""
    assert data["has_content"] is False


def test_generate_section_first_time(client: TestClient, seed_subject_topic, monkeypatch):
    subj, topic = seed_subject_topic
    user = _signup(client, "gen_first")
    token = user["access_token"]

    db, gen = _test_db()
    try:
        from app.models.user import User
        uobj = db.query(User).filter(User.id == user["user"]["id"]).first()
        uobj.credits = 100
        db.commit()
    finally:
        gen.close()

    async def mock_generate(subject, topic, section_index, previous_sections):
        return f"<h3>Generated section {section_index}</h3>"

    monkeypatch.setattr("app.routes.api.textbook.generate_section_content", mock_generate)

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        with patch("app.routes.api.textbook.TextbookService.cache_section", new_callable=AsyncMock) as mock_cache:
            resp = client.post(
                f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/0/generate",
                headers={"Authorization": f"Bearer {token}"},
                json={},
            )

    assert resp.status_code == 200
    data = resp.json()
    assert data["section_index"] == 0
    assert data["content"] == "<h3>Generated section 0</h3>"
    assert data["has_more"] is True


def test_generate_section_cached(client: TestClient, seed_subject_topic, monkeypatch):
    subj, topic = seed_subject_topic
    user = _signup(client, "gen_cached")
    token = user["access_token"]

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = "<h3>Cached Content</h3>"
        resp = client.post(
            f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/0/generate",
            headers={"Authorization": f"Bearer {token}"},
            json={},
        )
    assert resp.status_code == 200
    assert resp.json()["content"] == "<h3>Cached Content</h3>"


def test_generate_section_regeneration(client: TestClient, seed_subject_topic, monkeypatch):
    subj, topic = seed_subject_topic
    user = _signup(client, "gen_regen")
    token = user["access_token"]

    db, gen = _test_db()
    try:
        from app.models.user import User
        uobj = db.query(User).filter(User.id == user["user"]["id"]).first()
        uobj.credits = 100
        db.commit()
    finally:
        gen.close()

    async def mock_generate(subject, topic, section_index, previous_sections):
        return "<h3>Regenerated Content</h3>"

    monkeypatch.setattr("app.routes.api.textbook.generate_section_content", mock_generate)

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = "<h3>Old Content</h3>"

        with patch("app.routes.api.textbook.TextbookService.cache_section", new_callable=AsyncMock):
            resp = client.post(
                f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/0/generate",
                headers={"Authorization": f"Bearer {token}"},
                json={"regenerate": True},
            )
    assert resp.status_code == 200
    assert resp.json()["content"] == "<h3>Regenerated Content</h3>"


def test_generate_section_credit_deduction(client: TestClient, seed_subject_topic, monkeypatch):
    subj, topic = seed_subject_topic
    user = _signup(client, "gen_credit")
    token = user["access_token"]

    db, gen = _test_db()
    try:
        from app.models.user import User
        uobj = db.query(User).filter(User.id == user["user"]["id"]).first()
        uobj.credits = 0
        uobj.weekly_credits_used = 0
        db.commit()
    finally:
        gen.close()

    async def mock_generate(subject, topic, section_index, previous_sections):
        return "<h3>Content</h3>"

    monkeypatch.setattr("app.routes.api.textbook.generate_section_content", mock_generate)

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None

        with patch("app.routes.api.textbook.TextbookService.cache_section", new_callable=AsyncMock):
            resp = client.post(
                f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/0/generate",
                headers={"Authorization": f"Bearer {token}"},
                json={},
            )
    assert resp.status_code == 402


def test_generate_section_out_of_range(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "gen_oob")
    token = user["access_token"]
    resp = client.post(
        f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/99/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert resp.status_code == 404


def test_generate_section_last_has_more_false(client: TestClient, seed_subject_topic, monkeypatch):
    subj, topic = seed_subject_topic
    user = _signup(client, "gen_last")
    token = user["access_token"]

    db, gen = _test_db()
    try:
        from app.models.user import User
        uobj = db.query(User).filter(User.id == user["user"]["id"]).first()
        uobj.credits = 100
        db.commit()
    finally:
        gen.close()

    async def mock_generate(subject, topic, section_index, previous_sections):
        return "<h3>Last</h3>"

    monkeypatch.setattr("app.routes.api.textbook.generate_section_content", mock_generate)

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        with patch("app.routes.api.textbook.TextbookService.cache_section", new_callable=AsyncMock):
            resp = client.post(
                f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/9/generate",
                headers={"Authorization": f"Bearer {token}"},
                json={},
            )
    assert resp.json()["has_more"] is False


def test_section_plan_structure(client: TestClient):
    assert len(TEXTBOOK_SECTIONS) == 10
    for i, sec in enumerate(TEXTBOOK_SECTIONS):
        assert sec["index"] == i
        assert "title" in sec
        assert "focus" in sec


def test_cache_behaviour_miss(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "cache_miss")
    token = user["access_token"]

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        resp = client.get(
            f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/3",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.json()["has_content"] is False
    assert resp.json()["content"] == ""


def test_cache_behaviour_hit(client: TestClient, seed_subject_topic):
    subj, topic = seed_subject_topic
    user = _signup(client, "cache_hit")
    token = user["access_token"]

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = "<p>Cached!</p>"
        resp = client.get(
            f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/0",
            headers={"Authorization": f"Bearer {token}"},
        )
    assert resp.json()["content"] == "<p>Cached!</p>"
    assert resp.json()["has_content"] is True


def test_generate_section_ai_failure(client: TestClient, seed_subject_topic, monkeypatch):
    subj, topic = seed_subject_topic
    user = _signup(client, "gen_fail")
    token = user["access_token"]

    db, gen = _test_db()
    try:
        from app.models.user import User
        uobj = db.query(User).filter(User.id == user["user"]["id"]).first()
        uobj.credits = 100
        db.commit()
    finally:
        gen.close()

    async def mock_generate_fail(subject, topic, section_index, previous_sections):
        raise ValueError("AI generation failed")

    monkeypatch.setattr("app.routes.api.textbook.generate_section_content", mock_generate_fail)

    with patch("app.routes.api.textbook.TextbookService.get_cached_section", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = None
        with patch("app.routes.api.textbook.TextbookService.cache_section", new_callable=AsyncMock):
            resp = client.post(
                f"/api/subjects/{subj.slug}/topics/{topic.id}/textbook/sections/0/generate",
                headers={"Authorization": f"Bearer {token}"},
                json={},
            )
    assert resp.status_code == 502
