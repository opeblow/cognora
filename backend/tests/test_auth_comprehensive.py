import pytest
from datetime import timedelta, datetime, timezone
from fastapi.testclient import TestClient
from jose import jwt

from app.core.security import create_access_token, create_refresh_token, _make_jwt
from app.core.config import settings
from app.models.user import User, EmailVerification, PasswordReset
from app.utils.email import EmailService


# ---------------------------------------------------------------------------
# Autouse fixtures  (mock_redis is already autouse in conftest.py)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    monkeypatch.setattr(EmailService, "send_verification_email", lambda self, to, token: True)
    monkeypatch.setattr(EmailService, "send_password_reset_email", lambda self, to, token: True)
    monkeypatch.setattr(EmailService, "__init__", lambda self: None)


from app.main import app

_AUTH_BASE = "/api/auth"


def _signup(client, email="a@b.com", password="ValidPass123!", name="Test User"):
    return client.post(f"{_AUTH_BASE}/signup", json={
        "email": email, "password": password, "full_name": name,
    })


def _login(client, email="a@b.com", password="ValidPass123!"):
    return client.post(f"{_AUTH_BASE}/login", json={
        "email": email, "password": password,
    })


def _auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


def _get_token(resp) -> str:
    return resp.json()["access_token"]


def _get_refresh(resp) -> str:
    return resp.json()["refresh_token"]


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------

class TestSignup:
    def test_signup_success(self, client: TestClient):
        resp = _signup(client)
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "a@b.com"
        assert data["user"]["full_name"] == "Test User"
        assert data["user"]["is_verified"] is False
        assert data["user"]["credits"] == 50

    def test_signup_duplicate_email(self, client: TestClient):
        _signup(client, email="dup@b.com")
        resp = _signup(client, email="dup@b.com")
        assert resp.status_code == 400
        assert "already" in resp.json()["detail"].lower()

    def test_signup_weak_password_short(self, client: TestClient):
        resp = _signup(client, password="Ab1!")
        assert resp.status_code == 422

    def test_signup_empty_email(self, client: TestClient):
        resp = _signup(client, email="")
        assert resp.status_code == 422

    def test_signup_empty_password(self, client: TestClient):
        resp = _signup(client, password="")
        assert resp.status_code == 422

    def test_signup_empty_name(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/signup", json={
            "email": "emptyname@b.com", "password": "ValidPass123!", "full_name": "",
        })
        assert resp.status_code == 422

    def test_signup_xss_in_name(self, client: TestClient):
        malicious = "<script>alert('xss')</script>"
        resp = _signup(client, name=malicious)
        assert resp.status_code == 201
        assert resp.json()["user"]["full_name"] == malicious

    def test_signup_sql_injection_in_email(self, client: TestClient):
        payloads = ["' OR '1'='1", "'; DROP TABLE users; --", "admin'--"]
        for payload in payloads:
            resp = _signup(client, email=payload)
            assert resp.status_code in (201, 422), f"Failed for payload: {payload}"

    def test_signup_sql_injection_in_name(self, client: TestClient):
        payload = "'; DROP TABLE users; --"
        resp = _signup(client, name=payload)
        assert resp.status_code == 201
        assert resp.json()["user"]["full_name"] == payload

    def test_signup_email_too_long(self, client: TestClient):
        resp = _signup(client, email=f"{'a' * 300}@b.com")
        assert resp.status_code == 422

    def test_signup_password_too_long(self, client: TestClient):
        resp = _signup(client, password="A" * 200)
        assert resp.status_code == 422

    def test_signup_name_too_long(self, client: TestClient):
        resp = _signup(client, name="A" * 300)
        assert resp.status_code == 422

    def test_signup_unicode_in_name(self, client: TestClient):
        resp = _signup(client, name="José 中文")
        assert resp.status_code == 201


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:
    def test_login_success(self, client: TestClient):
        _signup(client, email="logintest@b.com")
        resp = _login(client, email="logintest@b.com")
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["email"] == "logintest@b.com"

    def test_login_wrong_password(self, client: TestClient):
        _signup(client, email="wrongpwd@b.com")
        resp = client.post(f"{_AUTH_BASE}/login", json={
            "email": "wrongpwd@b.com", "password": "WrongPass123!",
        })
        assert resp.status_code == 401
        assert "invalid" in resp.json()["detail"].lower()

    def test_login_non_existent_user(self, client: TestClient):
        resp = _login(client, email="nobody@b.com")
        assert resp.status_code == 401

    def test_login_disabled_account(self, client: TestClient, db_session):
        _signup(client, email="disabled@b.com")
        user = db_session.query(User).filter(User.email == "disabled@b.com").first()
        user.is_active = False
        db_session.commit()
        resp = _login(client, email="disabled@b.com")
        assert resp.status_code == 401
        assert "disabled" in resp.json()["detail"].lower()

    def test_login_empty_email(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/login", json={"email": "", "password": "x"})
        assert resp.status_code == 422

    def test_login_empty_password(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/login", json={"email": "a@b.com", "password": ""})
        assert resp.status_code == 422

    def test_login_case_sensitivity_email(self, client: TestClient):
        _signup(client, email="CaseSensitive@b.com")
        resp = _login(client, email="casesensitive@b.com")
        assert resp.status_code == 401

    def test_login_updates_last_active(self, client: TestClient, db_session):
        _signup(client, email="lastactive@b.com")
        user = db_session.query(User).filter(User.email == "lastactive@b.com").first()
        prev_active = user.last_active_at
        resp = _login(client, email="lastactive@b.com")
        assert resp.status_code == 200
        db_session.refresh(user)
        assert user.last_active_at is not None
        if prev_active:
            assert user.last_active_at > prev_active


# ---------------------------------------------------------------------------
# Get Me
# ---------------------------------------------------------------------------

class TestGetMe:
    def test_get_me_valid_token(self, client: TestClient):
        signup_resp = _signup(client, email="getme@b.com")
        token = _get_token(signup_resp)
        resp = client.get(f"{_AUTH_BASE}/me", headers=_auth_header(token))
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "getme@b.com"
        assert data["full_name"] == "Test User"
        assert "credits" in data

    def test_get_me_expired_token(self, client: TestClient):
        expired = create_access_token({"sub": "any", "email": "x"}, expires_delta=timedelta(days=-1))
        resp = client.get(f"{_AUTH_BASE}/me", headers=_auth_header(expired))
        assert resp.status_code == 401
        assert "expired" in resp.json()["detail"].lower()

    def test_get_me_malformed_token(self, client: TestClient):
        resp = client.get(f"{_AUTH_BASE}/me", headers=_auth_header("not.a.valid.token"))
        assert resp.status_code == 401

    def test_get_me_missing_auth_header(self, client: TestClient):
        resp = client.get(f"{_AUTH_BASE}/me")
        assert resp.status_code == 401

    def test_get_me_empty_token(self, client: TestClient):
        resp = client.get(f"{_AUTH_BASE}/me", headers=_auth_header(""))
        assert resp.status_code == 401

    def test_get_me_token_for_nonexistent_user(self, client: TestClient):
        fake_token = create_access_token({"sub": "nonexistent-id", "email": "fake@b.com"})
        resp = client.get(f"{_AUTH_BASE}/me", headers=_auth_header(fake_token))
        assert resp.status_code == 401

    def test_get_me_token_for_disabled_user(self, client: TestClient, db_session):
        signup_resp = _signup(client, email="disabledme@b.com")
        token = _get_token(signup_resp)
        user = db_session.query(User).filter(User.email == "disabledme@b.com").first()
        user.is_active = False
        db_session.commit()
        resp = client.get(f"{_AUTH_BASE}/me", headers=_auth_header(token))
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Refresh Token
# ---------------------------------------------------------------------------

class TestRefreshToken:
    def test_refresh_valid(self, client: TestClient):
        signup_resp = _signup(client, email="refresh@b.com")
        refresh = _get_refresh(signup_resp)
        resp = client.post(f"{_AUTH_BASE}/refresh", json={"refresh_token": refresh})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_expired(self, client: TestClient):
        expired_refresh = _make_jwt({"sub": "any", "type": "refresh"}, timedelta(days=-1))
        resp = client.post(f"{_AUTH_BASE}/refresh", json={"refresh_token": expired_refresh})
        assert resp.status_code == 401

    def test_refresh_invalid_format(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/refresh", json={"refresh_token": "not-a-valid-token"})
        assert resp.status_code == 401

    def test_refresh_empty_string(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/refresh", json={"refresh_token": ""})
        assert resp.status_code == 401

    def test_refresh_with_access_token(self, client: TestClient):
        signup_resp = _signup(client, email="accesstoken@b.com")
        access = _get_token(signup_resp)
        resp = client.post(f"{_AUTH_BASE}/refresh", json={"refresh_token": access})
        assert resp.status_code == 401

    def test_refresh_for_disabled_user(self, client: TestClient, db_session):
        signup_resp = _signup(client, email="refreshdisabled@b.com")
        refresh = _get_refresh(signup_resp)
        user = db_session.query(User).filter(User.email == "refreshdisabled@b.com").first()
        user.is_active = False
        db_session.commit()
        resp = client.post(f"{_AUTH_BASE}/refresh", json={"refresh_token": refresh})
        assert resp.status_code == 401

    def test_refresh_for_deleted_user(self, client: TestClient, db_session):
        signup_resp = _signup(client, email="refreshdeleted@b.com")
        refresh = _get_refresh(signup_resp)
        user = db_session.query(User).filter(User.email == "refreshdeleted@b.com").first()
        db_session.delete(user)
        db_session.commit()
        resp = client.post(f"{_AUTH_BASE}/refresh", json={"refresh_token": refresh})
        assert resp.status_code == 401

    def test_refresh_nonexistent_user_token(self, client: TestClient):
        token = create_refresh_token({"sub": "nonexistent", "type": "refresh"})
        resp = client.post(f"{_AUTH_BASE}/refresh", json={"refresh_token": token})
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Change Password
# ---------------------------------------------------------------------------

class TestChangePassword:
    def test_change_password_success(self, client: TestClient):
        signup_resp = _signup(client, email="changepwd@b.com")
        token = _get_token(signup_resp)
        resp = client.post(
            f"{_AUTH_BASE}/change-password",
            json={"current_password": "ValidPass123!", "new_password": "NewValid456!"},
            headers=_auth_header(token),
        )
        assert resp.status_code == 200

    def test_change_password_wrong_current(self, client: TestClient):
        signup_resp = _signup(client, email="wrongcurrent@b.com")
        token = _get_token(signup_resp)
        resp = client.post(
            f"{_AUTH_BASE}/change-password",
            json={"current_password": "WrongPass123!", "new_password": "NewValid456!"},
            headers=_auth_header(token),
        )
        assert resp.status_code == 400

    def test_change_password_login_with_new(self, client: TestClient):
        signup_resp = _signup(client, email="newlogin@b.com")
        token = _get_token(signup_resp)
        client.post(
            f"{_AUTH_BASE}/change-password",
            json={"current_password": "ValidPass123!", "new_password": "NewValid456!"},
            headers=_auth_header(token),
        )
        assert _login(client, email="newlogin@b.com", password="ValidPass123!").status_code == 401
        assert _login(client, email="newlogin@b.com", password="NewValid456!").status_code == 200

    def test_change_password_weak_new(self, client: TestClient):
        signup_resp = _signup(client, email="weaknew@b.com")
        token = _get_token(signup_resp)
        resp = client.post(
            f"{_AUTH_BASE}/change-password",
            json={"current_password": "ValidPass123!", "new_password": "Ab1!"},
            headers=_auth_header(token),
        )
        assert resp.status_code == 422

    def test_change_password_empty_new(self, client: TestClient):
        signup_resp = _signup(client, email="emptynew@b.com")
        token = _get_token(signup_resp)
        resp = client.post(
            f"{_AUTH_BASE}/change-password",
            json={"current_password": "ValidPass123!", "new_password": ""},
            headers=_auth_header(token),
        )
        assert resp.status_code == 422

    def test_change_password_requires_auth(self, client: TestClient):
        resp = client.post(
            f"{_AUTH_BASE}/change-password",
            json={"current_password": "x", "new_password": "NewValid456!"},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Forgot Password
# ---------------------------------------------------------------------------

class TestForgotPassword:
    def test_forgot_password_existing_email(self, client: TestClient):
        _signup(client, email="forgot@b.com")
        resp = client.post(f"{_AUTH_BASE}/forgot-password", json={"email": "forgot@b.com"})
        assert resp.status_code == 200

    def test_forgot_password_nonexistent_email(self, client: TestClient):
        """Security best practice: always returns 200 to prevent user enumeration."""
        resp = client.post(f"{_AUTH_BASE}/forgot-password", json={"email": "nobody@b.com"})
        assert resp.status_code == 200

    def test_forgot_password_empty_email(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/forgot-password", json={"email": ""})
        assert resp.status_code == 422

    def test_forgot_password_creates_reset_record(self, client: TestClient, db_session):
        _signup(client, email="forgotrecord@b.com")
        client.post(f"{_AUTH_BASE}/forgot-password", json={"email": "forgotrecord@b.com"})
        user = db_session.query(User).filter(User.email == "forgotrecord@b.com").first()
        resets = db_session.query(PasswordReset).filter(PasswordReset.user_id == user.id).all()
        assert len(resets) == 1
        assert resets[0].is_used is False

    def test_forgot_password_multiple_tokens(self, client: TestClient, db_session):
        _signup(client, email="multiforgot@b.com")
        for _ in range(3):
            client.post(f"{_AUTH_BASE}/forgot-password", json={"email": "multiforgot@b.com"})
        user = db_session.query(User).filter(User.email == "multiforgot@b.com").first()
        resets = db_session.query(PasswordReset).filter(PasswordReset.user_id == user.id).all()
        assert len(resets) == 3


# ---------------------------------------------------------------------------
# Reset Password
# ---------------------------------------------------------------------------

class TestResetPassword:
    def _get_reset_token(self, db_session, email):
        user = db_session.query(User).filter(User.email == email).first()
        if not user:
            return None
        reset = db_session.query(PasswordReset).filter(
            PasswordReset.user_id == user.id, PasswordReset.is_used == False
        ).first()
        return reset.token if reset else None

    def test_reset_password_success(self, client: TestClient, db_session):
        _signup(client, email="reset@b.com")
        client.post(f"{_AUTH_BASE}/forgot-password", json={"email": "reset@b.com"})
        token = self._get_reset_token(db_session, "reset@b.com")
        assert token is not None
        resp = client.post(f"{_AUTH_BASE}/reset-password", json={
            "token": token, "password": "NewReset123!",
        })
        assert resp.status_code == 200
        assert _login(client, email="reset@b.com", password="NewReset123!").status_code == 200

    def test_reset_password_expired_token(self, client: TestClient, db_session):
        _signup(client, email="resetexpired@b.com")
        client.post(f"{_AUTH_BASE}/forgot-password", json={"email": "resetexpired@b.com"})
        reset = db_session.query(PasswordReset).join(User).filter(
            User.email == "resetexpired@b.com"
        ).first()
        reset.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()
        resp = client.post(f"{_AUTH_BASE}/reset-password", json={
            "token": reset.token, "password": "NewReset123!",
        })
        assert resp.status_code == 400
        assert "expired" in resp.json()["detail"].lower()

    def test_reset_password_already_used(self, client: TestClient, db_session):
        _signup(client, email="resetused@b.com")
        client.post(f"{_AUTH_BASE}/forgot-password", json={"email": "resetused@b.com"})
        token = self._get_reset_token(db_session, "resetused@b.com")
        resp1 = client.post(f"{_AUTH_BASE}/reset-password", json={
            "token": token, "password": "NewReset123!",
        })
        assert resp1.status_code == 200
        resp2 = client.post(f"{_AUTH_BASE}/reset-password", json={
            "token": token, "password": "AnotherPass456!",
        })
        assert resp2.status_code == 400

    def test_reset_password_weak(self, client: TestClient, db_session):
        _signup(client, email="resetweak@b.com")
        client.post(f"{_AUTH_BASE}/forgot-password", json={"email": "resetweak@b.com"})
        token = self._get_reset_token(db_session, "resetweak@b.com")
        resp = client.post(f"{_AUTH_BASE}/reset-password", json={
            "token": token, "password": "Ab1!",
        })
        assert resp.status_code == 422

    def test_reset_password_invalid_token(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/reset-password", json={
            "token": "bogus-token", "password": "NewReset123!",
        })
        assert resp.status_code == 400

    def test_reset_password_empty_token(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/reset-password", json={
            "token": "", "password": "NewReset123!",
        })
        assert resp.status_code == 400

    def test_reset_password_empty_password(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/reset-password", json={
            "token": "some-token", "password": "",
        })
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Verify Email
# ---------------------------------------------------------------------------

class TestVerifyEmail:
    def _get_verify_token(self, db_session, email):
        user = db_session.query(User).filter(User.email == email).first()
        if not user:
            return None
        verify = db_session.query(EmailVerification).filter(
            EmailVerification.user_id == user.id, EmailVerification.is_used == False
        ).first()
        return verify.token if verify else None

    def test_verify_email_success(self, client: TestClient, db_session):
        _signup(client, email="verify@b.com")
        token = self._get_verify_token(db_session, "verify@b.com")
        assert token is not None
        resp = client.post(f"{_AUTH_BASE}/verify-email", json={"token": token})
        assert resp.status_code == 200
        user = db_session.query(User).filter(User.email == "verify@b.com").first()
        assert user.is_verified is True

    def test_verify_email_expired_token(self, client: TestClient, db_session):
        _signup(client, email="verifyexpired@b.com")
        verify = db_session.query(EmailVerification).join(User).filter(
            User.email == "verifyexpired@b.com"
        ).first()
        verify.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
        db_session.commit()
        resp = client.post(f"{_AUTH_BASE}/verify-email", json={"token": verify.token})
        assert resp.status_code == 400
        assert "expired" in resp.json()["detail"].lower()

    def test_verify_email_already_used(self, client: TestClient, db_session):
        _signup(client, email="verifyused@b.com")
        token = self._get_verify_token(db_session, "verifyused@b.com")
        assert client.post(f"{_AUTH_BASE}/verify-email", json={"token": token}).status_code == 200
        resp2 = client.post(f"{_AUTH_BASE}/verify-email", json={"token": token})
        assert resp2.status_code == 400

    def test_verify_email_double_use_prevention(self, client: TestClient, db_session):
        _signup(client, email="verifydouble@b.com")
        token = self._get_verify_token(db_session, "verifydouble@b.com")
        client.post(f"{_AUTH_BASE}/verify-email", json={"token": token})
        verify = db_session.query(EmailVerification).filter(
            EmailVerification.token == token
        ).first()
        assert verify.is_used is True

    def test_verify_email_invalid_token(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/verify-email", json={"token": "bogus-token"})
        assert resp.status_code == 400

    def test_verify_email_empty_token(self, client: TestClient):
        resp = client.post(f"{_AUTH_BASE}/verify-email", json={"token": ""})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Google OAuth
# ---------------------------------------------------------------------------

class TestGoogleOAuth:
    def test_google_login_returns_auth_url(self, client: TestClient):
        resp = client.get(f"{_AUTH_BASE}/google/login")
        assert resp.status_code == 200
        data = resp.json()
        assert "auth_url" in data
        assert data["auth_url"].startswith("https://accounts.google.com/o/oauth2/v2/auth")

    def test_google_callback_with_error(self, client: TestClient):
        resp = client.get(f"{_AUTH_BASE}/google/callback?code=ignored&error=access_denied")
        assert resp.status_code == 400
        assert "failed" in resp.json()["detail"].lower()

    def test_google_callback_no_code(self, client: TestClient):
        resp = client.get(f"{_AUTH_BASE}/google/callback")
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Token Expiration Edge Cases
# ---------------------------------------------------------------------------

class TestTokenExpiration:
    def test_access_token_expires_as_configured(self, client: TestClient):
        signup_resp = _signup(client, email="tokenexp@b.com")
        token = _get_token(signup_resp)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        expected = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        assert abs((exp - expected).total_seconds()) < 5

    def test_refresh_token_expires_as_configured(self, client: TestClient):
        signup_resp = _signup(client, email="refreshexp@b.com")
        refresh = _get_refresh(signup_resp)
        payload = jwt.decode(refresh, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "exp" in payload
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        expected = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        assert abs((exp - expected).total_seconds()) < 5

    def test_token_jti_present(self, client: TestClient):
        signup_resp = _signup(client, email="jtitest@b.com")
        token = _get_token(signup_resp)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert "jti" in payload

    def test_token_contains_sub_and_email(self, client: TestClient):
        signup_resp = _signup(client, email="claims@b.com")
        token = _get_token(signup_resp)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] is not None
        assert payload["email"] == "claims@b.com"


# ---------------------------------------------------------------------------
# Auth Dependency Edge Cases
# ---------------------------------------------------------------------------

class TestAuthDependency:
    def test_protected_route_with_bearer_no_token(self, client: TestClient):
        resp = client.get(f"{_AUTH_BASE}/me", headers={"Authorization": "Bearer "})
        assert resp.status_code == 401

    def test_protected_route_without_bearer_prefix(self, client: TestClient):
        signup_resp = _signup(client, email="nobearer@b.com")
        token = _get_token(signup_resp)
        resp = client.get(f"{_AUTH_BASE}/me", headers={"Authorization": token})
        assert resp.status_code == 401
