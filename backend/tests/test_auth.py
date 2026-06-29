import pytest
from fastapi.testclient import TestClient


def test_signup(client: TestClient):
    response = client.post("/api/auth/signup", json={
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_signup_duplicate_email(client: TestClient):
    client.post("/api/auth/signup", json={
        "email": "duplicate@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    response = client.post("/api/auth/signup", json={
        "email": "duplicate@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    assert response.status_code == 400


def test_login_success(client: TestClient):
    client.post("/api/auth/signup", json={
        "email": "login@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    response = client.post("/api/auth/login", json={
        "email": "login@example.com",
        "password": "TestPassword123!",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login_invalid_password(client: TestClient):
    client.post("/api/auth/signup", json={
        "email": "invalidpwd@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    response = client.post("/api/auth/login", json={
        "email": "invalidpwd@example.com",
        "password": "WrongPassword123!",
    })
    assert response.status_code == 401


def test_get_me(client: TestClient):
    signup_resp = client.post("/api/auth/signup", json={
        "email": "me@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    token = signup_resp.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"


def test_refresh_token(client: TestClient):
    signup_resp = client.post("/api/auth/signup", json={
        "email": "refresh@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    refresh_token = signup_resp.json()["refresh_token"]

    response = client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_change_password(client: TestClient):
    signup_resp = client.post("/api/auth/signup", json={
        "email": "changepwd@example.com",
        "password": "OldPassword123!",
        "full_name": "Test User",
    })
    token = signup_resp.json()["access_token"]

    response = client.post("/api/auth/change-password", json={
        "current_password": "OldPassword123!",
        "new_password": "NewPassword123!",
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_forgot_password(client: TestClient):
    client.post("/api/auth/signup", json={
        "email": "forgot@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    response = client.post("/api/auth/forgot-password", json={
        "email": "forgot@example.com",
    })
    assert response.status_code == 200


def test_auth_required(client: TestClient):
    response = client.get("/api/auth/me")
    assert response.status_code == 403 or response.status_code == 401
