import pytest
from fastapi.testclient import TestClient


def test_credit_balance(client: TestClient):
    signup_resp = client.post("/api/auth/signup", json={
        "email": "credittest@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    token = signup_resp.json()["access_token"]

    response = client.get("/api/credits/balance", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert "credits" in data
    assert "weekly_credits_used" in data
