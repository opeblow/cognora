import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class PasswordMixin:
    @staticmethod
    def validate_password_strength(password: str) -> str:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(password) > 128:
            raise ValueError("Password must not exceed 128 characters")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\\\;'/`~]", password):
            raise ValueError("Password must contain at least one special character")
        return password


class SignUpRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return PasswordMixin.validate_password_strength(v)


class LoginRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return PasswordMixin.validate_password_strength(v)


class VerifyEmailRequest(BaseModel):
    token: str


class GoogleAuthRequest(BaseModel):
    code: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    avatar_url: Optional[str] = None
    is_verified: bool
    credits: str
    learning_streak: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        return PasswordMixin.validate_password_strength(v)
