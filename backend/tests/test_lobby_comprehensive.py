import pytest
from fastapi.testclient import TestClient
from app.main import app


def _signup(client: TestClient, email: str, suffix: str = "") -> dict:
    tag = f"{email}_{suffix}" if suffix else email
    resp = client.post("/api/auth/signup", json={
        "email": f"lobby_{tag}@example.com",
        "password": "TestPass123!",
        "full_name": f"Lobby User {email}",
    })
    return resp.json()


def test_create_lobby_valid(client: TestClient):
    user = _signup(client, "create_valid")
    token = user["access_token"]
    resp = client.post("/api/lobbies", json={
        "name": "Math Study Group",
        "subject": "Mathematics",
        "topic": "Algebra",
        "max_participants": 10,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Math Study Group"
    assert data["is_active"] is True
    assert data["subject"] == "Mathematics"
    assert data["max_participants"] == 10
    assert data["created_by"] == user["user"]["id"]


def test_create_lobby_default_max_participants(client: TestClient):
    user = _signup(client, "create_defmax")
    token = user["access_token"]
    resp = client.post("/api/lobbies", json={
        "name": "Default Max",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["max_participants"] == 10


def test_create_lobby_min_max_participants(client: TestClient):
    user = _signup(client, "create_minmax")
    token = user["access_token"]
    resp = client.post("/api/lobbies", json={
        "name": "Small Group",
        "max_participants": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["max_participants"] == 1


def test_create_lobby_large_max_participants(client: TestClient):
    user = _signup(client, "create_bigmax")
    token = user["access_token"]
    resp = client.post("/api/lobbies", json={
        "name": "Large Group",
        "max_participants": 1000,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["max_participants"] == 1000


def test_create_lobby_missing_name(client: TestClient):
    user = _signup(client, "create_nameless")
    token = user["access_token"]
    resp = client.post("/api/lobbies", json={
        "subject": "Physics",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


def test_create_lobby_unauthenticated(client: TestClient):
    resp = client.post("/api/lobbies", json={"name": "Test"})
    assert resp.status_code in (401, 403)


def test_list_lobbies_empty(client: TestClient):
    resp = client.get("/api/lobbies")
    assert resp.status_code == 200
    data = resp.json()
    assert data["lobbies"] == []
    assert data["total"] == 0


def test_list_lobbies_with_lobbies(client: TestClient):
    user = _signup(client, "list_with")
    token = user["access_token"]
    client.post("/api/lobbies", json={"name": "Group A"}, headers={"Authorization": f"Bearer {token}"})
    client.post("/api/lobbies", json={"name": "Group B"}, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/api/lobbies")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert any(l["name"] == "Group A" for l in data["lobbies"])


def test_list_lobbies_only_active(client: TestClient):
    user = _signup(client, "list_active")
    token = user["access_token"]
    c1 = client.post("/api/lobbies", json={"name": "Active Lobby"}, headers={"Authorization": f"Bearer {token}"})
    lobby_id = c1.json()["id"]
    client.post("/api/lobbies", json={"name": "To Close"}, headers={"Authorization": f"Bearer {token}"})

    client.post(f"/api/lobbies/{lobby_id}/close", headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/api/lobbies")
    names = [l["name"] for l in resp.json()["lobbies"]]
    assert "Active Lobby" not in names
    assert "To Close" in names


def test_get_lobby_existing(client: TestClient):
    user = _signup(client, "get_exist")
    token = user["access_token"]
    create = client.post("/api/lobbies", json={"name": "My Lobby"}, headers={"Authorization": f"Bearer {token}"})
    lobby_id = create.json()["id"]

    resp = client.get(f"/api/lobbies/{lobby_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "My Lobby"


def test_get_lobby_not_found(client: TestClient):
    resp = client.get("/api/lobbies/nonexistent_id")
    assert resp.status_code == 404


def test_get_lobby_inactive(client: TestClient):
    user = _signup(client, "get_inact")
    token = user["access_token"]
    create = client.post("/api/lobbies", json={"name": "Temp"}, headers={"Authorization": f"Bearer {token}"})
    lobby_id = create.json()["id"]
    client.post(f"/api/lobbies/{lobby_id}/close", headers={"Authorization": f"Bearer {token}"})

    resp = client.get(f"/api/lobbies/{lobby_id}")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_close_lobby_owner(client: TestClient):
    user = _signup(client, "close_owner")
    token = user["access_token"]
    create = client.post("/api/lobbies", json={"name": "Mine"}, headers={"Authorization": f"Bearer {token}"})
    lobby_id = create.json()["id"]

    resp = client.post(f"/api/lobbies/{lobby_id}/close", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["message"] == "Lobby closed"

    get = client.get(f"/api/lobbies/{lobby_id}")
    assert get.json()["is_active"] is False


def test_close_lobby_not_owner(client: TestClient):
    owner = _signup(client, "close_not_owner")
    otok = owner["access_token"]
    other = _signup(client, "close_not_other")
    otok2 = other["access_token"]

    create = client.post("/api/lobbies", json={"name": "Not Yours"}, headers={"Authorization": f"Bearer {otok}"})
    lobby_id = create.json()["id"]

    resp = client.post(f"/api/lobbies/{lobby_id}/close", headers={"Authorization": f"Bearer {otok2}"})
    assert resp.status_code == 404


def test_close_lobby_already_closed(client: TestClient):
    user = _signup(client, "close_aldone")
    token = user["access_token"]
    create = client.post("/api/lobbies", json={"name": "Done Deal"}, headers={"Authorization": f"Bearer {token}"})
    lobby_id = create.json()["id"]
    client.post(f"/api/lobbies/{lobby_id}/close", headers={"Authorization": f"Bearer {token}"})

    resp = client.post(f"/api/lobbies/{lobby_id}/close", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_get_history_empty(client: TestClient):
    user = _signup(client, "hist_empty")
    token = user["access_token"]
    create = client.post("/api/lobbies", json={"name": "Quiet"}, headers={"Authorization": f"Bearer {token}"})
    lobby_id = create.json()["id"]

    resp = client.get(f"/api/lobbies/{lobby_id}/history")
    assert resp.status_code == 200
    data = resp.json()
    assert data["messages"] == []


def test_get_history_with_messages(client: TestClient, monkeypatch):
    user = _signup(client, "hist_msgs")
    token = user["access_token"]
    create = client.post("/api/lobbies", json={"name": "Chatty"}, headers={"Authorization": f"Bearer {token}"})
    lobby_id = create.json()["id"]

    from app.database.base import get_db as original_get_db
    from app.services.lobby_service import StudyLobbyService
    gen = app.dependency_overrides[original_get_db]()
    db = next(gen)
    try:
        svc = StudyLobbyService(db)
        svc.save_message(lobby_id, user["user"]["id"], "User1", "Hello", is_ai_response=False)
        svc.save_message(lobby_id, None, "Cognora AI", "Hi there!", is_ai_response=True)
    finally:
        try:
            gen.close()
        except Exception:
            pass

    resp = client.get(f"/api/lobbies/{lobby_id}/history")
    assert resp.status_code == 200
    messages = resp.json()["messages"]
    assert len(messages) == 2
    assert any(m["username"] == "Cognora AI" and m["is_ai_response"] for m in messages)


def test_get_history_limit(client: TestClient):
    user = _signup(client, "hist_lim")
    token = user["access_token"]
    create = client.post("/api/lobbies", json={"name": "Lots"}, headers={"Authorization": f"Bearer {token}"})
    lobby_id = create.json()["id"]

    from app.database.base import get_db as original_get_db
    from app.services.lobby_service import StudyLobbyService
    gen = app.dependency_overrides[original_get_db]()
    db = next(gen)
    try:
        svc = StudyLobbyService(db)
        for i in range(5):
            svc.save_message(lobby_id, user["user"]["id"], "User", f"Msg {i}")
    finally:
        try:
            gen.close()
        except Exception:
            pass

    resp = client.get(f"/api/lobbies/{lobby_id}/history?limit=2")
    assert len(resp.json()["messages"]) == 2


def test_lobby_list_pagination(client: TestClient):
    user = _signup(client, "list_pag")
    token = user["access_token"]
    for i in range(5):
        client.post("/api/lobbies", json={"name": f"Lobby{i}"}, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/api/lobbies?skip=0&limit=2")
    assert resp.status_code == 200
    assert len(resp.json()["lobbies"]) == 2


def test_create_lobby_without_subject_or_topic(client: TestClient):
    user = _signup(client, "no_subj_topic")
    token = user["access_token"]
    resp = client.post("/api/lobbies", json={"name": "General Study"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["subject"] is None
    assert resp.json()["topic"] is None


def test_get_lobby_history_not_found(client: TestClient):
    user = _signup(client, "hist_nf")
    token = user["access_token"]
    resp = client.get("/api/lobbies/nonexistent/history", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["messages"] == []
