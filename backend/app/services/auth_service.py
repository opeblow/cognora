import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.repositories.user import UserRepository, EmailVerificationRepository, PasswordResetRepository
from app.models.user import User
from app.utils.email import EmailService
from typing import Optional
import secrets


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.email_verification_repo = EmailVerificationRepository(db)
        self.password_reset_repo = PasswordResetRepository(db)
        self.db = db

    def signup(self, email: str, password: str, full_name: str) -> dict:
        existing = self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        user = self.user_repo.create(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            credits=50,
            weekly_credits_used=0,
            weekly_credits_reset_at=datetime.now(timezone.utc) + timedelta(days=7)
        )

        verification_token = secrets.token_urlsafe(48)
        self.email_verification_repo.create(
            user_id=user.id,
            token=verification_token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
        )

        email_service = EmailService()
        email_service.send_verification_email(user.email, verification_token)

        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "type": "refresh"})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "is_verified": user.is_verified,
                "credits": user.credits,
                "learning_streak": user.learning_streak
            }
        }

    def login(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not user.password_hash:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if not user.is_active:
            raise ValueError("Account is disabled")

        user.last_active_at = datetime.now(timezone.utc)
        self.db.commit()

        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        refresh_token = create_refresh_token({"sub": str(user.id), "type": "refresh"})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "is_verified": user.is_verified,
                "credits": user.credits,
                "learning_streak": user.learning_streak
            }
        }

    def verify_email(self, token: str) -> bool:
        verification = self.email_verification_repo.get_by_token(token)
        if not verification or verification.is_used:
            raise ValueError("Invalid or expired verification token")

        if verification.expires_at < datetime.now(timezone.utc):
            raise ValueError("Verification token expired")

        verification.is_used = True
        user = self.user_repo.get(verification.user_id)
        if user:
            user.is_verified = True
        self.db.commit()
        return True

    def forgot_password(self, email: str) -> bool:
        user = self.user_repo.get_by_email(email)
        if not user:
            return True

        token = secrets.token_urlsafe(48)
        self.password_reset_repo.create(
            user_id=user.id,
            token=token,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )

        email_service = EmailService()
        email_service.send_password_reset_email(user.email, token)

        return True

    def reset_password(self, token: str, new_password: str) -> bool:
        reset = self.password_reset_repo.get_by_token(token)
        if not reset or reset.is_used:
            raise ValueError("Invalid or expired reset token")

        if reset.expires_at < datetime.now(timezone.utc):
            raise ValueError("Reset token expired")

        reset.is_used = True
        user = self.user_repo.get(reset.user_id)
        if user:
            user.password_hash = hash_password(new_password)
        self.db.commit()
        return True

    def refresh_token(self, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")

        user_id = payload.get("sub")
        user = self.user_repo.get(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive")

        access_token = create_access_token({"sub": str(user.id), "email": user.email})
        new_refresh_token = create_refresh_token({"sub": str(user.id), "type": "refresh"})

        return {"access_token": access_token, "refresh_token": new_refresh_token}

    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        user = self.user_repo.get(user_id)
        if not user or not user.password_hash:
            raise ValueError("Invalid password")

        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        user.password_hash = hash_password(new_password)
        self.db.commit()
        return True

    def get_google_auth_url(self) -> str:
        from urllib.parse import urlencode
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

    def google_auth(self, code: str) -> dict:
        import httpx

        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise ValueError("Google OAuth is not configured")

        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        with httpx.Client() as client:
            token_resp = client.post("https://oauth2.googleapis.com/token", data=token_data)
            if token_resp.status_code != 200:
                raise ValueError("Failed to exchange authorization code")

            token_json = token_resp.json()
            access_token = token_json.get("access_token")

            user_resp = client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            if user_resp.status_code != 200:
                raise ValueError("Failed to get user info")

            google_user = user_resp.json()

        google_id = google_user["id"]
        email = google_user["email"]
        full_name = google_user.get("name", email.split("@")[0])
        avatar_url = google_user.get("picture")

        user = self.user_repo.get_by_google_id(google_id)
        if not user:
            user = self.user_repo.get_by_email(email)

        if user:
            if not user.google_id:
                user.google_id = google_id
            if not user.avatar_url:
                user.avatar_url = avatar_url
            if not user.is_verified:
                user.is_verified = True
            user.last_active_at = datetime.now(timezone.utc)
            self.db.commit()
        else:
            user = self.user_repo.create(
                email=email,
                full_name=full_name,
                google_id=google_id,
                avatar_url=avatar_url,
                is_verified=True,
                credits=50,
                weekly_credits_used=0,
                weekly_credits_reset_at=datetime.now(timezone.utc) + timedelta(days=7),
            )

        jwt_access = create_access_token({"sub": str(user.id), "email": user.email})
        jwt_refresh = create_refresh_token({"sub": str(user.id), "type": "refresh"})

        return {
            "access_token": jwt_access,
            "refresh_token": jwt_refresh,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "is_verified": user.is_verified,
                "credits": user.credits,
                "learning_streak": user.learning_streak,
            },
        }
