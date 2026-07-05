import pytest
from fastapi.testclient import TestClient


def _signup(client: TestClient, email: str) -> dict:
    resp = client.post("/api/auth/signup", json={
        "email": email,
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    assert resp.status_code == 201
    return resp.json()


def _token(resp: dict) -> str:
    return resp["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------- get_settings ----------

def test_get_settings_default(client: TestClient):
    resp = _signup(client, "settings_default@test.com")
    token = _token(resp)

    response = client.get("/api/settings", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["notifications"]["study_reminder_enabled"] is True
    assert data["notifications"]["study_reminder_time"] == "09:00"
    assert data["notifications"]["quiz_reminder_enabled"] is True
    assert data["notifications"]["email_notifications"] is True
    assert data["academic"]["exam_focus"] == "JAMB"
    assert data["academic"]["preferred_subjects"] == []
    assert data["academic"]["difficulty_preference"] == "medium"
    assert data["preferences"]["timezone"] == "Africa/Lagos"


def test_get_settings_after_updates(client: TestClient):
    resp = _signup(client, "settings_after@test.com")
    token = _token(resp)

    client.put("/api/settings/notifications", headers=_auth_header(token), json={
        "study_reminder_enabled": False,
        "study_reminder_time": "14:30",
    })
    client.put("/api/settings/academic", headers=_auth_header(token), json={
        "exam_focus": "WAEC",
        "difficulty_preference": "hard",
    })
    client.put("/api/settings/preferences", headers=_auth_header(token), json={
        "timezone": "America/New_York",
    })

    response = client.get("/api/settings", headers=_auth_header(token))
    data = response.json()
    assert data["notifications"]["study_reminder_enabled"] is False
    assert data["notifications"]["study_reminder_time"] == "14:30"
    assert data["academic"]["exam_focus"] == "WAEC"
    assert data["academic"]["difficulty_preference"] == "hard"
    assert data["preferences"]["timezone"] == "America/New_York"


# ---------- update_notifications ----------

def test_update_notifications_all_fields(client: TestClient):
    resp = _signup(client, "notif_all@test.com")
    token = _token(resp)

    response = client.put("/api/settings/notifications", headers=_auth_header(token), json={
        "study_reminder_enabled": False,
        "study_reminder_time": "07:00",
        "quiz_reminder_enabled": False,
        "email_notifications": False,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["notifications"]["study_reminder_enabled"] is False
    assert data["notifications"]["study_reminder_time"] == "07:00"
    assert data["notifications"]["quiz_reminder_enabled"] is False
    assert data["notifications"]["email_notifications"] is False


def test_update_notifications_partial(client: TestClient):
    resp = _signup(client, "notif_partial@test.com")
    token = _token(resp)

    response = client.put("/api/settings/notifications", headers=_auth_header(token), json={
        "study_reminder_time": "10:15",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["notifications"]["study_reminder_time"] == "10:15"
    assert data["notifications"]["study_reminder_enabled"] is True


def test_update_notifications_empty_body(client: TestClient):
    resp = _signup(client, "notif_empty@test.com")
    token = _token(resp)

    response = client.put("/api/settings/notifications", headers=_auth_header(token), json={})
    assert response.status_code == 200
    data = response.json()
    assert data["notifications"]["study_reminder_enabled"] is True


def test_update_notifications_invalid_time_format(client: TestClient):
    resp = _signup(client, "notif_badtime@test.com")
    token = _token(resp)

    response = client.put("/api/settings/notifications", headers=_auth_header(token), json={
        "study_reminder_time": "25:00",
    })
    assert response.status_code == 200


def test_update_notifications_invalid_types(client: TestClient):
    resp = _signup(client, "notif_badtype@test.com")
    token = _token(resp)

    response = client.put("/api/settings/notifications", headers=_auth_header(token), json={
        "study_reminder_enabled": "not-a-boolean",
    })
    assert response.status_code == 422


# ---------- update_academic_preferences ----------

def test_update_academic_preferences_valid(client: TestClient):
    resp = _signup(client, "acad_valid@test.com")
    token = _token(resp)

    response = client.put("/api/settings/academic", headers=_auth_header(token), json={
        "exam_focus": "NECO",
        "preferred_subjects": ["Mathematics", "English"],
        "difficulty_preference": "easy",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["academic"]["exam_focus"] == "NECO"
    assert data["academic"]["preferred_subjects"] == ["Mathematics", "English"]
    assert data["academic"]["difficulty_preference"] == "easy"


def test_update_academic_preferences_empty_subjects(client: TestClient):
    resp = _signup(client, "acad_emptysubj@test.com")
    token = _token(resp)

    response = client.put("/api/settings/academic", headers=_auth_header(token), json={
        "preferred_subjects": [],
    })
    assert response.status_code == 200
    assert response.json()["academic"]["preferred_subjects"] == []


def test_update_academic_preferences_null_subjects(client: TestClient):
    resp = _signup(client, "acad_nullsubj@test.com")
    token = _token(resp)

    response = client.put("/api/settings/academic", headers=_auth_header(token), json={
        "preferred_subjects": None,
    })
    assert response.status_code == 200


def test_update_academic_preferences_partial(client: TestClient):
    resp = _signup(client, "acad_partial@test.com")
    token = _token(resp)

    response = client.put("/api/settings/academic", headers=_auth_header(token), json={
        "difficulty_preference": "hard",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["academic"]["difficulty_preference"] == "hard"
    assert data["academic"]["exam_focus"] == "JAMB"


# ---------- update_preferences ----------

def test_update_preferences_valid_timezone(client: TestClient):
    resp = _signup(client, "pref_tz_ok@test.com")
    token = _token(resp)

    response = client.put("/api/settings/preferences", headers=_auth_header(token), json={
        "timezone": "Europe/London",
    })
    assert response.status_code == 200
    assert response.json()["preferences"]["timezone"] == "Europe/London"


def test_update_preferences_invalid_timezone(client: TestClient):
    resp = _signup(client, "pref_tz_bad@test.com")
    token = _token(resp)

    response = client.put("/api/settings/preferences", headers=_auth_header(token), json={
        "timezone": "Not/A/Real/Timezone",
    })
    assert response.status_code == 200


def test_update_preferences_empty_body(client: TestClient):
    resp = _signup(client, "pref_empty@test.com")
    token = _token(resp)

    response = client.put("/api/settings/preferences", headers=_auth_header(token), json={})
    assert response.status_code == 200
    assert response.json()["preferences"]["timezone"] == "Africa/Lagos"


# ---------- change_password ----------

def test_change_password_correct(client: TestClient):
    resp = _signup(client, "chpwd_correct@test.com")
    token = _token(resp)

    response = client.post("/api/settings/change-password", headers=_auth_header(token), json={
        "current_password": "TestPassword123!",
        "new_password": "NewSecurePass456!",
    })
    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"


def test_change_password_incorrect_current(client: TestClient):
    resp = _signup(client, "chpwd_wrong@test.com")
    token = _token(resp)

    response = client.post("/api/settings/change-password", headers=_auth_header(token), json={
        "current_password": "WrongPassword!",
        "new_password": "NewSecurePass456!",
    })
    assert response.status_code == 400
    assert "incorrect" in response.json()["detail"].lower()


def test_change_password_too_short(client: TestClient):
    resp = _signup(client, "chpwd_short@test.com")
    token = _token(resp)

    response = client.post("/api/settings/change-password", headers=_auth_header(token), json={
        "current_password": "TestPassword123!",
        "new_password": "Ab1",
    })
    assert response.status_code == 400


# ---------- Auto-create settings on first access ----------

def test_auto_create_settings_on_first_access(client: TestClient):
    resp = _signup(client, "auto_first@test.com")
    token = _token(resp)

    response = client.get("/api/settings", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["notifications"]["study_reminder_enabled"] is True
    assert data["academic"]["exam_focus"] == "JAMB"
    assert data["preferences"]["timezone"] == "Africa/Lagos"


def test_auto_create_then_update(client: TestClient):
    resp = _signup(client, "auto_then@test.com")
    token = _token(resp)

    get1 = client.get("/api/settings", headers=_auth_header(token))
    assert get1.json()["notifications"]["study_reminder_time"] == "09:00"

    client.put("/api/settings/notifications", headers=_auth_header(token), json={
        "study_reminder_time": "11:00",
    })

    get2 = client.get("/api/settings", headers=_auth_header(token))
    assert get2.json()["notifications"]["study_reminder_time"] == "11:00"


# ---------- Settings persistence across calls ----------

def test_settings_persistence_across_calls(client: TestClient):
    resp = _signup(client, "persist@test.com")
    token = _token(resp)

    client.put("/api/settings/academic", headers=_auth_header(token), json={
        "exam_focus": "WAEC",
        "preferred_subjects": ["Physics"],
    })

    for _ in range(5):
        response = client.get("/api/settings", headers=_auth_header(token))
        data = response.json()
        assert data["academic"]["exam_focus"] == "WAEC"
        assert data["academic"]["preferred_subjects"] == ["Physics"]


def test_settings_isolation_between_users(client: TestClient):
    resp1 = _signup(client, "iso_set1@test.com")
    token1 = _token(resp1)

    resp2 = _signup(client, "iso_set2@test.com")
    token2 = _token(resp2)

    client.put("/api/settings/academic", headers=_auth_header(token1), json={
        "exam_focus": "WAEC",
    })

    d1 = client.get("/api/settings", headers=_auth_header(token1)).json()
    assert d1["academic"]["exam_focus"] == "WAEC"

    d2 = client.get("/api/settings", headers=_auth_header(token2)).json()
    assert d2["academic"]["exam_focus"] == "JAMB"


# ---------- Unauthorized access ----------

def test_get_settings_unauthorized(client: TestClient):
    response = client.get("/api/settings")
    assert response.status_code == 401 or response.status_code == 403


def test_update_notifications_unauthorized(client: TestClient):
    response = client.put("/api/settings/notifications", json={
        "study_reminder_enabled": False,
    })
    assert response.status_code == 401 or response.status_code == 403


def test_change_password_unauthorized(client: TestClient):
    response = client.post("/api/settings/change-password", json={
        "current_password": "x",
        "new_password": "y",
    })
    assert response.status_code == 401 or response.status_code == 403
