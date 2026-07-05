import pytest
from fastapi.testclient import TestClient


def _signup(client: TestClient, email: str, suffix: str = "") -> dict:
    resp = client.post("/api/auth/signup", json={
        "email": f"live_{email}_{suffix}@example.com" if suffix else f"live_{email}@example.com",
        "password": "TestPass123!",
        "full_name": f"User {email}",
    })
    return resp.json()


def test_create_room_valid(client: TestClient):
    user = _signup(client, "create_valid")
    token = user["access_token"]
    resp = client.post("/api/live/rooms", json={
        "subject": "Mathematics",
        "topic": "Algebra",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["room_id"].startswith("room_")
    assert data["provider"] == "mock"
    assert data["status"] == "pending"
    assert data["token"] is not None


def test_create_room_with_student_id(client: TestClient):
    tutor = _signup(client, "createstu_tutor")
    student = _signup(client, "createstu_student")
    token = tutor["access_token"]
    resp = client.post("/api/live/rooms", json={
        "subject": "Physics",
        "topic": "Kinematics",
        "student_id": student["user"]["id"],
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "pending"


def test_create_room_missing_subject(client: TestClient):
    user = _signup(client, "create_nosubj")
    token = user["access_token"]
    resp = client.post("/api/live/rooms", json={
        "topic": "Algebra",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422


def test_create_room_unauthenticated(client: TestClient):
    resp = client.post("/api/live/rooms", json={
        "subject": "Mathematics",
    })
    assert resp.status_code in (401, 403)


def test_get_room_existing(client: TestClient):
    user = _signup(client, "get_exist")
    token = user["access_token"]
    create = client.post("/api/live/rooms", json={
        "subject": "Chemistry",
    }, headers={"Authorization": f"Bearer {token}"})
    room_id = create.json()["room_id"]

    resp = client.get(f"/api/live/rooms/{room_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["room_id"] == room_id
    assert data["subject"] == "Chemistry"


def test_get_room_not_found(client: TestClient):
    user = _signup(client, "get_notfound")
    token = user["access_token"]
    resp = client.get("/api/live/rooms/nonexistent_room", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_get_room_access_denied_as_student(client: TestClient):
    tutor = _signup(client, "access_tutor")
    ttok = tutor["access_token"]
    student = _signup(client, "access_student")
    stok = student["access_token"]

    create = client.post("/api/live/rooms", json={
        "subject": "Biology",
    }, headers={"Authorization": f"Bearer {ttok}"})
    room_id = create.json()["room_id"]

    resp = client.get(f"/api/live/rooms/{room_id}", headers={"Authorization": f"Bearer {stok}"})
    assert resp.status_code == 403


def test_get_room_access_granted_as_student_invited(client: TestClient):
    tutor = _signup(client, "accessinv_tutor")
    ttok = tutor["access_token"]
    student = _signup(client, "accessinv_student")

    create = client.post("/api/live/rooms", json={
        "subject": "Chemistry",
        "student_id": student["user"]["id"],
    }, headers={"Authorization": f"Bearer {ttok}"})
    room_id = create.json()["room_id"]

    stok = student["access_token"]
    resp = client.get(f"/api/live/rooms/{room_id}", headers={"Authorization": f"Bearer {stok}"})
    assert resp.status_code == 200


def test_start_session_valid(client: TestClient):
    user = _signup(client, "start_valid")
    token = user["access_token"]
    create = client.post("/api/live/rooms", json={
        "subject": "Mathematics",
    }, headers={"Authorization": f"Bearer {token}"})
    room_id = create.json()["room_id"]

    resp = client.post(f"/api/live/rooms/{room_id}/start", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "active"
    assert data["started_at"] is not None


def test_start_session_not_your_room(client: TestClient):
    tutor = _signup(client, "startnr_tutor")
    ttok = tutor["access_token"]
    other = _signup(client, "startnr_other")
    otok = other["access_token"]

    create = client.post("/api/live/rooms", json={
        "subject": "Physics",
    }, headers={"Authorization": f"Bearer {ttok}"})
    room_id = create.json()["room_id"]

    resp = client.post(f"/api/live/rooms/{room_id}/start", headers={"Authorization": f"Bearer {otok}"})
    assert resp.status_code == 404


def test_start_session_already_started(client: TestClient):
    user = _signup(client, "start_already")
    token = user["access_token"]
    create = client.post("/api/live/rooms", json={
        "subject": "Mathematics",
    }, headers={"Authorization": f"Bearer {token}"})
    room_id = create.json()["room_id"]

    client.post(f"/api/live/rooms/{room_id}/start", headers={"Authorization": f"Bearer {token}"})
    resp = client.post(f"/api/live/rooms/{room_id}/start", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "active"


def test_start_session_not_found(client: TestClient):
    user = _signup(client, "start_nf")
    token = user["access_token"]
    resp = client.post("/api/live/rooms/nonexistent/start", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_end_session_valid(client: TestClient):
    user = _signup(client, "end_valid")
    token = user["access_token"]
    create = client.post("/api/live/rooms", json={
        "subject": "Mathematics",
    }, headers={"Authorization": f"Bearer {token}"})
    room_id = create.json()["room_id"]
    client.post(f"/api/live/rooms/{room_id}/start", headers={"Authorization": f"Bearer {token}"})

    resp = client.post(f"/api/live/rooms/{room_id}/end", json={
        "recording_url": "https://example.com/recording.mp4",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "completed"
    assert data["recording_url"] == "https://example.com/recording.mp4"
    assert data["ended_at"] is not None


def test_end_session_without_recording(client: TestClient):
    user = _signup(client, "end_norec")
    token = user["access_token"]
    create = client.post("/api/live/rooms", json={
        "subject": "English",
    }, headers={"Authorization": f"Bearer {token}"})
    room_id = create.json()["room_id"]
    client.post(f"/api/live/rooms/{room_id}/start", headers={"Authorization": f"Bearer {token}"})

    resp = client.post(f"/api/live/rooms/{room_id}/end", json={}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["recording_url"] is None


def test_end_session_not_found(client: TestClient):
    user = _signup(client, "end_nf")
    token = user["access_token"]
    resp = client.post("/api/live/rooms/nonexistent/end", json={}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_end_session_not_your_room(client: TestClient):
    tutor = _signup(client, "endnr_tutor")
    ttok = tutor["access_token"]
    other = _signup(client, "endnr_other")
    otok = other["access_token"]

    create = client.post("/api/live/rooms", json={
        "subject": "Physics",
    }, headers={"Authorization": f"Bearer {ttok}"})
    room_id = create.json()["room_id"]

    resp = client.post(f"/api/live/rooms/{room_id}/end", json={}, headers={"Authorization": f"Bearer {otok}"})
    assert resp.status_code == 404


def test_list_sessions_as_tutor(client: TestClient):
    user = _signup(client, "list_tutor")
    token = user["access_token"]
    client.post("/api/live/rooms", json={"subject": "Math"}, headers={"Authorization": f"Bearer {token}"})
    client.post("/api/live/rooms", json={"subject": "Physics"}, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/api/live?role=tutor", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_list_sessions_as_student(client: TestClient):
    tutor = _signup(client, "liststu_tutor")
    ttok = tutor["access_token"]
    student = _signup(client, "liststu_student")

    client.post("/api/live/rooms", json={
        "subject": "Chemistry",
        "student_id": student["user"]["id"],
    }, headers={"Authorization": f"Bearer {ttok}"})

    stok = student["access_token"]
    resp = client.get("/api/live?role=student", headers={"Authorization": f"Bearer {stok}"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_list_sessions_empty(client: TestClient):
    user = _signup(client, "list_empty")
    token = user["access_token"]
    resp = client.get("/api/live?role=tutor", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_sessions_pagination(client: TestClient):
    user = _signup(client, "list_pag")
    token = user["access_token"]
    for i in range(5):
        client.post("/api/live/rooms", json={"subject": f"Subject{i}"}, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/api/live?role=tutor&skip=0&limit=2", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_sessions_unauthenticated(client: TestClient):
    resp = client.get("/api/live?role=tutor")
    assert resp.status_code in (401, 403)


def test_provider_default_mock(client: TestClient):
    user = _signup(client, "prov_mock")
    token = user["access_token"]
    resp = client.post("/api/live/rooms", json={
        "subject": "Mathematics",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.json()["provider"] == "mock"
    assert resp.json()["room_id"].startswith("room_")


def test_room_id_format(client: TestClient):
    user = _signup(client, "roomfmt")
    token = user["access_token"]
    resp = client.post("/api/live/rooms", json={
        "subject": "English",
    }, headers={"Authorization": f"Bearer {token}"})
    room_id = resp.json()["room_id"]
    assert room_id.startswith("room_")
    assert len(room_id) > 5
    assert room_id == resp.json()["provider_room_id"]


def test_create_room_none_topic(client: TestClient):
    user = _signup(client, "notopic")
    token = user["access_token"]
    resp = client.post("/api/live/rooms", json={
        "subject": "Biology",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "pending"


def test_list_sessions_supports_skip_limit(client: TestClient):
    user = _signup(client, "skplim")
    token = user["access_token"]
    for i in range(3):
        client.post("/api/live/rooms", json={"subject": f"S{i}"}, headers={"Authorization": f"Bearer {token}"})

    r1 = client.get("/api/live?role=tutor&skip=0&limit=1", headers={"Authorization": f"Bearer {token}"})
    r2 = client.get("/api/live?role=tutor&skip=1&limit=1", headers={"Authorization": f"Bearer {token}"})
    assert len(r1.json()) == 1
    assert len(r2.json()) == 1
    assert r1.json()[0]["room_id"] != r2.json()[0]["room_id"]
