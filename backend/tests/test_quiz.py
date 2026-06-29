import pytest
from fastapi.testclient import TestClient


def test_get_quizzes(client: TestClient):
    signup_resp = client.post("/api/auth/signup", json={
        "email": "quiztest@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    token = signup_resp.json()["access_token"]

    response = client.get("/api/quizzes", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "quizzes" in data
    assert "total" in data
