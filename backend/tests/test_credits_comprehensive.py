import pytest
from datetime import timedelta, datetime, timezone
from fastapi.testclient import TestClient

from app.core.config import settings
from app.database.base import get_db
from app.models.user import User
from app.models.credit import CreditTransaction
from app.services.credit_service import CreditService
from app.services.credit_policy import TrialCreditPolicy, PaidCreditPolicy

from app.main import app


# ---------------------------------------------------------------------------
# Autouse fixtures (mock_redis is already autouse in conftest.py)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    monkeypatch.setattr("app.utils.email.EmailService.__init__", lambda self: None)
    monkeypatch.setattr("app.utils.email.EmailService.send_verification_email", lambda self, to, token: True)
    monkeypatch.setattr("app.utils.email.EmailService.send_password_reset_email", lambda self, to, token: True)


@pytest.fixture
def user_token(client, db_session):
    resp = client.post("/api/auth/signup", json={
        "email": "credits@test.com", "password": "ValidPass123!", "full_name": "Credit User",
    })
    assert resp.status_code == 201
    data = resp.json()
    return data["access_token"], data["refresh_token"], data["user"]["id"]


@pytest.fixture
def auth_headers(user_token):
    token, _, _ = user_token
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def credit_service(db_session):
    return CreditService(db_session)


_CREDITS_BASE = "/api/credits"


# ---------------------------------------------------------------------------
# Get Balance
# ---------------------------------------------------------------------------

class TestGetBalance:
    def test_initial_balance(self, client: TestClient, auth_headers):
        resp = client.get(f"{_CREDITS_BASE}/balance", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["credits"] == 50
        assert data["plan"] == "trial"
        assert data["is_trial"] is True
        assert data["weekly_credits_total"] == settings.FREE_WEEKLY_CREDITS
        assert "transactions" in data

    def test_balance_structure(self, client: TestClient, auth_headers):
        resp = client.get(f"{_CREDITS_BASE}/balance", headers=auth_headers)
        data = resp.json()
        assert "plan" in data
        assert "credits" in data
        assert "weekly_credits_used" in data
        assert "weekly_credits_total" in data
        assert "is_trial" in data
        assert "transactions" in data

    def test_zero_balance_scenario(self, client: TestClient, db_session, user_token):
        token, _, user_id = user_token
        headers = {"Authorization": f"Bearer {token}"}
        user = db_session.query(User).filter(User.id == user_id).first()
        user.credits = 0
        db_session.commit()
        resp = client.get(f"{_CREDITS_BASE}/balance", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["credits"] == 0

    def test_balance_with_transactions(self, client: TestClient, auth_headers):
        client.post(f"{_CREDITS_BASE}/purchase", json={"amount": 100}, headers=auth_headers)
        resp = client.get(f"{_CREDITS_BASE}/balance", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["credits"] >= 150
        assert len(data["transactions"]) >= 1

    def test_balance_negative_credits(self, client: TestClient, db_session, user_token):
        token, _, user_id = user_token
        headers = {"Authorization": f"Bearer {token}"}
        user = db_session.query(User).filter(User.id == user_id).first()
        user.credits = -5
        db_session.commit()
        resp = client.get(f"{_CREDITS_BASE}/balance", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["credits"] == -5

    def test_balance_requires_auth(self, client: TestClient):
        resp = client.get(f"{_CREDITS_BASE}/balance")
        assert resp.status_code == 401

    def test_balance_nonexistent_user(self, client: TestClient):
        from app.core.security import create_access_token
        fake_token = create_access_token({"sub": "nonexistent", "email": "x"})
        resp = client.get(f"{_CREDITS_BASE}/balance", headers={"Authorization": f"Bearer {fake_token}"})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Purchase Credits
# ---------------------------------------------------------------------------

class TestPurchase:
    def test_purchase_valid_amount(self, client: TestClient, auth_headers):
        resp = client.post(f"{_CREDITS_BASE}/purchase", json={"amount": 100}, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "100 credits added" in data["message"]
        assert data["balance"]["credits"] >= 150

    def test_purchase_zero_amount(self, client: TestClient, auth_headers):
        resp = client.post(f"{_CREDITS_BASE}/purchase", json={"amount": 0}, headers=auth_headers)
        assert resp.status_code == 400
        assert "positive" in resp.json()["detail"].lower()

    def test_purchase_negative_amount(self, client: TestClient, auth_headers):
        resp = client.post(f"{_CREDITS_BASE}/purchase", json={"amount": -50}, headers=auth_headers)
        assert resp.status_code == 400

    def test_purchase_very_large_amount(self, client: TestClient, auth_headers):
        resp = client.post(f"{_CREDITS_BASE}/purchase", json={"amount": 999999}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["balance"]["credits"] >= 999999 + 50

    def test_purchase_adds_transaction(self, client: TestClient, db_session, auth_headers, user_token):
        _, _, user_id = user_token
        client.post(f"{_CREDITS_BASE}/purchase", json={"amount": 75}, headers=auth_headers)
        txns = db_session.query(CreditTransaction).filter(
            CreditTransaction.user_id == user_id, CreditTransaction.transaction_type == "purchase"
        ).all()
        assert len(txns) >= 1
        assert txns[0].amount == 75

    def test_purchase_with_reference(self, client: TestClient, auth_headers):
        resp = client.post(
            f"{_CREDITS_BASE}/purchase",
            json={"amount": 50, "reference": "paystack_ref_123"},
            headers=auth_headers,
        )
        assert resp.status_code == 200

    def test_purchase_requires_auth(self, client: TestClient):
        resp = client.post(f"{_CREDITS_BASE}/purchase", json={"amount": 50})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Deduct Credits (via service layer – no public /deduct endpoint)
# ---------------------------------------------------------------------------

class TestDeduct:
    def test_deduct_ai_ask(self, user_token, credit_service):
        _, _, user_id = user_token
        assert credit_service.deduct_credits(user_id, "ai_ask") is True

    def test_deduct_generate_quiz(self, user_token, credit_service):
        _, _, user_id = user_token
        assert credit_service.deduct_credits(user_id, "generate_quiz") is True

    def test_deduct_mock_exam(self, user_token, credit_service):
        _, _, user_id = user_token
        assert credit_service.deduct_credits(user_id, "mock_exam") is True

    def test_deduct_unknown_action(self, user_token, credit_service):
        _, _, user_id = user_token
        with pytest.raises(ValueError, match="unknown"):
            credit_service.deduct_credits(user_id, "unknown_action")

    def test_deduct_insufficient_credits(self, db_session, user_token, credit_service):
        _, _, user_id = user_token
        db_session.query(User).filter(User.id == user_id).first().credits = 0
        db_session.commit()
        with pytest.raises(ValueError, match="Insufficient"):
            credit_service.deduct_credits(user_id, "mock_exam")

    def test_deduct_reduces_balance(self, user_token, credit_service):
        _, _, user_id = user_token
        before = credit_service.get_balance(user_id)["credits"]
        credit_service.deduct_credits(user_id, "ai_ask")
        assert credit_service.get_balance(user_id)["credits"] == before - 1

    def test_deduct_multiple(self, user_token, credit_service):
        _, _, user_id = user_token
        credit_service.deduct_credits(user_id, "ai_ask")
        credit_service.deduct_credits(user_id, "generate_quiz")
        credit_service.deduct_credits(user_id, "mock_exam")
        assert credit_service.get_balance(user_id)["credits"] == 37

    def test_deduct_creates_transaction(self, db_session, user_token, credit_service):
        _, _, user_id = user_token
        credit_service.deduct_credits(user_id, "generate_quiz")
        txns = db_session.query(CreditTransaction).filter(
            CreditTransaction.user_id == user_id, CreditTransaction.transaction_type == "usage"
        ).all()
        assert len(txns) >= 1
        assert txns[0].amount == -2

    def test_deduct_nonexistent_user(self, credit_service):
        with pytest.raises(ValueError, match="User not found"):
            credit_service.deduct_credits("nonexistent-user-id", "ai_ask")

    def test_deduct_exact_balance(self, db_session, user_token, credit_service):
        _, _, user_id = user_token
        db_session.query(User).filter(User.id == user_id).first().credits = 1
        db_session.commit()
        credit_service.deduct_credits(user_id, "ai_ask")
        assert credit_service.get_balance(user_id)["credits"] == 0

    def test_deduct_sequential_until_empty(self, user_token, credit_service):
        _, _, user_id = user_token
        succeeded = 0
        for _ in range(60):
            try:
                credit_service.deduct_credits(user_id, "ai_ask")
                succeeded += 1
            except ValueError:
                break
        assert succeeded == 50


# ---------------------------------------------------------------------------
# Upgrade Plan
# ---------------------------------------------------------------------------

class TestUpgrade:
    def test_upgrade_to_paid(self, client: TestClient, auth_headers):
        resp = client.post(f"{_CREDITS_BASE}/upgrade", json={"plan": "paid"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["plan"] == "paid"

    def test_upgrade_to_trial(self, client: TestClient, auth_headers):
        resp = client.post(f"{_CREDITS_BASE}/upgrade", json={"plan": "trial"}, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["plan"] == "trial"

    def test_upgrade_invalid_plan(self, client: TestClient, auth_headers):
        resp = client.post(f"{_CREDITS_BASE}/upgrade", json={"plan": "premium_plus"}, headers=auth_headers)
        assert resp.status_code == 400
        assert "unknown" in resp.json()["detail"].lower()

    def test_upgrade_empty_plan(self, client: TestClient, auth_headers):
        resp = client.post(f"{_CREDITS_BASE}/upgrade", json={"plan": ""}, headers=auth_headers)
        assert resp.status_code == 400

    def test_upgrade_requires_auth(self, client: TestClient):
        resp = client.post(f"{_CREDITS_BASE}/upgrade", json={"plan": "paid"})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Credit Costs Endpoint
# ---------------------------------------------------------------------------

class TestCosts:
    def test_costs_endpoint(self, client: TestClient, auth_headers):
        resp = client.get(f"{_CREDITS_BASE}/costs", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["costs"]["ai_ask"] == 1
        assert data["costs"]["generate_quiz"] == 2
        assert data["costs"]["mock_exam"] == 10

    def test_costs_requires_auth(self, client: TestClient):
        resp = client.get(f"{_CREDITS_BASE}/costs")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Weekly Reset Logic
# ---------------------------------------------------------------------------

class TestWeeklyReset:
    def test_reset_weekly_if_needed_resets_used(self, client: TestClient, db_session, user_token):
        token, _, user_id = user_token
        headers = {"Authorization": f"Bearer {token}"}
        user = db_session.query(User).filter(User.id == user_id).first()
        user.weekly_credits_used = 40
        user.weekly_credits_reset_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
        client.get(f"{_CREDITS_BASE}/balance", headers=headers)
        db_session.refresh(user)
        assert user.weekly_credits_used == 0
        assert user.weekly_credits_reset_at.replace(tzinfo=timezone.utc) > datetime.now(timezone.utc)

    def test_reset_weekly_grants_free_credits_on_trial(self, client: TestClient, db_session, user_token):
        token, _, user_id = user_token
        headers = {"Authorization": f"Bearer {token}"}
        user = db_session.query(User).filter(User.id == user_id).first()
        user.credits = 10
        user.weekly_credits_used = 40
        user.weekly_credits_reset_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
        client.get(f"{_CREDITS_BASE}/balance", headers=headers)
        db_session.refresh(user)
        assert user.credits >= 10 + settings.FREE_WEEKLY_CREDITS

    def test_reset_weekly_not_needed(self, client: TestClient, db_session, user_token):
        token, _, user_id = user_token
        headers = {"Authorization": f"Bearer {token}"}
        user = db_session.query(User).filter(User.id == user_id).first()
        user.weekly_credits_used = 10
        user.weekly_credits_reset_at = datetime.now(timezone.utc) + timedelta(days=3)
        db_session.commit()
        client.get(f"{_CREDITS_BASE}/balance", headers=headers)
        db_session.refresh(user)
        assert user.weekly_credits_used == 10

    def test_reset_weekly_resets_used_and_grants_on_trial(self, client: TestClient, db_session, user_token):
        token, _, user_id = user_token
        headers = {"Authorization": f"Bearer {token}"}
        user = db_session.query(User).filter(User.id == user_id).first()
        user.credits = 10
        user.weekly_credits_used = 40
        user.weekly_credits_reset_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
        client.get(f"{_CREDITS_BASE}/balance", headers=headers)
        db_session.refresh(user)
        assert user.weekly_credits_used == 0
        assert user.credits == 10 + settings.FREE_WEEKLY_CREDITS


# ---------------------------------------------------------------------------
# Trial vs Paid Credit Policy Behavior
# ---------------------------------------------------------------------------

class TestCreditPolicyBehavior:
    def test_trial_tracking_via_service(self, db_session, user_token, credit_service):
        _, _, user_id = user_token
        user = db_session.query(User).filter(User.id == user_id).first()
        credit_service.deduct_credits(user_id, "ai_ask")
        db_session.refresh(user)
        assert user.weekly_credits_used == 1
        credit_service.deduct_credits(user_id, "generate_quiz")
        db_session.refresh(user)
        assert user.weekly_credits_used == 3

    def test_paid_policy_no_weekly_tracking(self, db_session, user_token):
        _, _, user_id = user_token
        from app.database.base import get_db as original_get_db
        gen = app.dependency_overrides[original_get_db]()
        s = next(gen)
        service = CreditService(s, policy=PaidCreditPolicy())
        service.deduct_credits(user_id, "ai_ask")
        s.close()
        user = db_session.query(User).filter(User.id == user_id).first()
        assert user.weekly_credits_used == 0

    def test_trial_balance_includes_weekly_info(self, client: TestClient, auth_headers):
        data = client.get(f"{_CREDITS_BASE}/balance", headers=auth_headers).json()
        assert data["plan"] == "trial"
        assert "weekly_credits_used" in data
        assert "weekly_credits_total" in data
        assert data["is_trial"] is True

    def test_paid_balance_omits_weekly_info(self, client: TestClient, auth_headers):
        client.post(f"{_CREDITS_BASE}/upgrade", json={"plan": "paid"}, headers=auth_headers)
        data = client.get(f"{_CREDITS_BASE}/balance", headers=auth_headers).json()
        assert data["is_trial"] is True


# ---------------------------------------------------------------------------
# Award Trial Bonus
# ---------------------------------------------------------------------------

class TestAwardTrialBonus:
    def test_award_bonus_new_user(self, db_session, user_token, credit_service):
        _, _, user_id = user_token
        db_session.query(User).filter(User.id == user_id).first().credits = 0
        db_session.commit()
        assert credit_service.award_trial_bonus(user_id) is True
        user = db_session.query(User).filter(User.id == user_id).first()
        assert user.credits == settings.FREE_WEEKLY_CREDITS

    def test_award_bonus_existing_user_with_credits(self, db_session, user_token, credit_service):
        _, _, user_id = user_token
        db_session.query(User).filter(User.id == user_id).first().credits = 25
        db_session.commit()
        assert credit_service.award_trial_bonus(user_id) is False
        assert db_session.query(User).filter(User.id == user_id).first().credits == 25

    def test_award_bonus_nonexistent_user(self, credit_service):
        with pytest.raises(ValueError):
            credit_service.award_trial_bonus("nonexistent-user-id")

    def test_award_bonus_creates_transaction(self, db_session, user_token, credit_service):
        _, _, user_id = user_token
        db_session.query(User).filter(User.id == user_id).first().credits = 0
        db_session.commit()
        credit_service.award_trial_bonus(user_id)
        txns = db_session.query(CreditTransaction).filter(
            CreditTransaction.user_id == user_id, CreditTransaction.transaction_type == "bonus"
        ).all()
        assert len(txns) >= 1


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_balance_after_upgrade_downgrade(self, client: TestClient, auth_headers):
        bal_before = client.get(f"{_CREDITS_BASE}/balance", headers=auth_headers).json()["credits"]
        upgrade_resp = client.post(f"{_CREDITS_BASE}/upgrade", json={"plan": "paid"}, headers=auth_headers)
        assert upgrade_resp.status_code == 200
        assert upgrade_resp.json()["plan"] == "paid"

    def test_purchase_then_upgrade_does_not_lose_credits(self, client: TestClient, auth_headers):
        client.post(f"{_CREDITS_BASE}/purchase", json={"amount": 200}, headers=auth_headers)
        client.post(f"{_CREDITS_BASE}/upgrade", json={"plan": "paid"}, headers=auth_headers)
        bal = client.get(f"{_CREDITS_BASE}/balance", headers=auth_headers).json()["credits"]
        assert bal >= 250

    def test_add_credits_via_service(self, user_token, credit_service):
        _, _, user_id = user_token
        credit_service.add_credits(user_id, 500, "Testing bulk add")
        assert credit_service.get_balance(user_id)["credits"] >= 550

    def test_add_negative_credits_via_service(self, user_token, credit_service):
        _, _, user_id = user_token
        credit_service.add_credits(user_id, -30, "Manual adjustment")
        assert credit_service.get_balance(user_id)["credits"] == 20

    def test_policy_default_is_trial(self, credit_service):
        assert credit_service.get_policy() == "trial"

    def test_policy_after_upgrade(self, db_session, user_token):
        _, _, user_id = user_token
        from app.database.base import get_db as original_get_db
        gen = app.dependency_overrides[original_get_db]()
        s = next(gen)
        service = CreditService(s)
        assert service.get_policy() == "trial"
        service.set_policy(PaidCreditPolicy())
        assert service.get_policy() == "paid"
        service.set_policy(TrialCreditPolicy())
        assert service.get_policy() == "trial"
        s.close()

    def test_deduct_until_exhaustion(self, user_token, credit_service):
        _, _, user_id = user_token
        for _ in range(50):
            credit_service.deduct_credits(user_id, "ai_ask")
        with pytest.raises(ValueError):
            credit_service.deduct_credits(user_id, "ai_ask")
