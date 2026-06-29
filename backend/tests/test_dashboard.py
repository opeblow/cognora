import pytest
from fastapi.testclient import TestClient


def test_dashboard(client: TestClient):
    signup_resp = client.post("/api/auth/signup", json={
        "email": "dashboardtest@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    token = signup_resp.json()["access_token"]

    response = client.get("/api/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "welcome_name" in data
    assert "credits" in data
    assert "learning_streak" in data
