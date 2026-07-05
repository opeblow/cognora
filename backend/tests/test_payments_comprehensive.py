import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.models.payment import Payment
from app.models.user import User
from app.services.paystack_service import CREDIT_PACKS


def _signup(client: TestClient, email: str) -> dict:
    resp = client.post("/api/auth/signup", json={
        "email": f"pay_{email}@example.com",
        "password": "TestPass123!",
        "full_name": f"Payment User {email}",
    })
    return resp.json()


def _set_paystack_keys(monkeypatch):
    monkeypatch.setattr("app.core.config.settings.PAYSTACK_SECRET_KEY", "sk_test_123")
    monkeypatch.setattr("app.core.config.settings.PAYSTACK_PUBLIC_KEY", "pk_test_123")


def _test_db():
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    return db, gen


def test_get_credit_packs(client: TestClient):
    resp = client.get("/api/payments/packs")
    assert resp.status_code == 200
    data = resp.json()
    assert "packs" in data
    expected = {str(k): v for k, v in CREDIT_PACKS.items()}
    assert data["packs"] == expected


def test_credit_pack_structure():
    assert CREDIT_PACKS == {50: 500, 100: 900, 200: 1600, 500: 3500, 1000: 6000}


def test_initiate_purchase_valid(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)

    mock_init = MagicMock(return_value={"authorization_url": "https://paystack.com/auth", "reference": "COG_testref123"})

    user = _signup(client, "init_valid")
    token = user["access_token"]

    with patch("app.services.paystack_service.PaystackService.initialize_transaction", mock_init):
        resp = client.post("/api/payments/purchase/initiate", json={
            "credit_amount": 100,
        }, headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 200
    data = resp.json()
    assert data["credit_amount"] == 100
    assert data["amount"] == CREDIT_PACKS[100]
    assert data["currency"] == "NGN"
    assert data["reference"].startswith("COG_")
    assert data["authorization_url"] == "https://paystack.com/auth"


def test_initiate_purchase_invalid_amount(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)
    user = _signup(client, "init_badamt")
    token = user["access_token"]

    resp = client.post("/api/payments/purchase/initiate", json={
        "credit_amount": 42,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
    assert "Invalid credit amount" in resp.json()["detail"]


def test_initiate_purchase_negative_amount(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)
    user = _signup(client, "init_neg")
    token = user["access_token"]

    resp = client.post("/api/payments/purchase/initiate", json={
        "credit_amount": -50,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400


def test_initiate_purchase_service_failure(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)

    mock_init = MagicMock(return_value=None)

    user = _signup(client, "init_fail")
    token = user["access_token"]

    with patch("app.services.paystack_service.PaystackService.initialize_transaction", mock_init):
        resp = client.post("/api/payments/purchase/initiate", json={
            "credit_amount": 100,
        }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400


def test_initiate_purchase_network_error(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)

    mock_err = MagicMock(side_effect=Exception("Network failure"))

    user = _signup(client, "init_netfail")
    token = user["access_token"]

    with patch("app.services.paystack_service.PaystackService.initialize_transaction", mock_err):
        resp = client.post("/api/payments/purchase/initiate", json={
            "credit_amount": 100,
        }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 500


def test_initiate_purchase_unauthenticated(client: TestClient):
    resp = client.post("/api/payments/purchase/initiate", json={"credit_amount": 100})
    assert resp.status_code in (401, 403)


def test_verify_payment_completed(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)

    mock_verify = MagicMock(return_value={"status": "success", "amount": 50000, "currency": "NGN"})

    user = _signup(client, "ver_ok")
    token = user["access_token"]
    db, gen = _test_db()
    try:
        pay = Payment(user_id=user["user"]["id"], amount="500", currency="NGN",
                      status="completed", reference="ref_ok", credits_purchased="100")
        db.add(pay)
        db.commit()
    finally:
        gen.close()

    with patch("app.services.paystack_service.PaystackService.verify_transaction", mock_verify):
        resp = client.get("/api/payments/verify/ref_ok", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "success"
    assert resp.json()["amount"] == 500.0


def test_verify_payment_pending(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)

    mock_verify = MagicMock(return_value=None)

    user = _signup(client, "ver_pend")
    token = user["access_token"]

    with patch("app.services.paystack_service.PaystackService.verify_transaction", mock_verify):
        resp = client.get("/api/payments/verify/ref_pending", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_verify_payment_not_found(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)
    user = _signup(client, "ver_nf")
    token = user["access_token"]

    mock_verify = MagicMock(return_value=None)

    with patch("app.services.paystack_service.PaystackService.verify_transaction", mock_verify):
        resp = client.get("/api/payments/verify/nonexistent", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_verify_payment_unauthenticated(client: TestClient):
    resp = client.get("/api/payments/verify/something")
    assert resp.status_code in (401, 403)


def test_webhook_charge_success(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)
    user = _signup(client, "wh_success")

    db, gen = _test_db()
    try:
        pay = Payment(user_id=user["user"]["id"], amount="500", currency="NGN",
                      status="pending", reference="wh_ref_1", credits_purchased="100")
        db.add(pay)
        db.commit()
        pay_id = pay.id
    finally:
        gen.close()

    payload = {
        "event": "charge.success",
        "data": {"reference": "wh_ref_1", "channel": "card"},
    }
    resp = client.post("/api/payments/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"

    db2, gen2 = _test_db()
    try:
        updated = db2.query(Payment).filter(Payment.id == pay_id).first()
        assert updated.status == "completed"
        assert updated.payment_method == "card"
    finally:
        gen2.close()


def test_webhook_wrong_event(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)

    payload = {
        "event": "charge.failed",
        "data": {"reference": "some_ref"},
    }
    resp = client.post("/api/payments/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored"


def test_webhook_duplicate_already_completed(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)
    user = _signup(client, "wh_dup")

    db, gen = _test_db()
    try:
        pay = Payment(user_id=user["user"]["id"], amount="500", currency="NGN",
                      status="completed", reference="wh_dup_ref", credits_purchased="100")
        db.add(pay)
        db.commit()
    finally:
        gen.close()

    payload = {
        "event": "charge.success",
        "data": {"reference": "wh_dup_ref", "channel": "card"},
    }
    resp = client.post("/api/payments/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_webhook_payment_not_found(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)

    payload = {
        "event": "charge.success",
        "data": {"reference": "nonexistent_ref", "channel": "card"},
    }
    resp = client.post("/api/payments/webhook", json=payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored"


def test_webhook_malformed_payload(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)
    resp = client.post("/api/payments/webhook", json={"garbage": True})
    assert resp.status_code == 200
    assert resp.json()["status"] == "ignored"


def test_initiate_purchase_creates_payment_record(client: TestClient, monkeypatch):
    _set_paystack_keys(monkeypatch)

    mock_init = MagicMock(return_value={"authorization_url": "https://paystack.com/go", "reference": "COG_recordtest"})

    user = _signup(client, "init_record")
    token = user["access_token"]

    with patch("app.services.paystack_service.PaystackService.initialize_transaction", mock_init):
        resp = client.post("/api/payments/purchase/initiate", json={
            "credit_amount": 200,
        }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    db, gen = _test_db()
    try:
        pay = db.query(Payment).filter(Payment.reference == "COG_recordtest").first()
        assert pay is not None
        assert pay.status == "pending"
        assert pay.credits_purchased == "200"
        assert pay.user_id == user["user"]["id"]
    finally:
        gen.close()


def test_paystack_not_configured(client: TestClient, monkeypatch):
    monkeypatch.setattr("app.core.config.settings.PAYSTACK_SECRET_KEY", "")
    user = _signup(client, "no_paystack")
    token = user["access_token"]

    resp = client.post("/api/payments/purchase/initiate", json={
        "credit_amount": 100,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
