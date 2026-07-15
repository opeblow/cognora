from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Cognora"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str = ""
    REDIS_URL: str = ""

    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = ""

    APP_URL: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "Cognora <noreply@cognora.app>"
    BRAVE_API_KEY: str = ""

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    FREE_WEEKLY_CREDITS: int = 50
    RATE_LIMIT_PER_MINUTE: int = 60

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_UPLOAD_TYPES: list[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/webp",
        "audio/webm",
        "audio/mp3",
        "audio/wav",
        "audio/mp4",
        "audio/ogg",
        "audio/x-m4a",
    ]

    WHISPER_MODEL: str = "whisper-1"
    AUDIO_MAX_DURATION_SECONDS: int = 300

    PAYSTACK_SECRET_KEY: str = ""
    PAYSTACK_PUBLIC_KEY: str = ""

    LIVE_SESSION_PROVIDER: str = "mock"
    HUNDREDMS_API_KEY: str = ""
    HUNDREDMS_API_SECRET: str = ""
    AGORA_APP_ID: str = ""
    AGORA_APP_CERTIFICATE: str = ""

    SENTRY_DSN: str = ""
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value):
        if isinstance(value, str) and value.lower() in {"release", "production", "prod"}:
            return False
        return value

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def check_cors(cls, value, info):
        debug = info.data.get("DEBUG", False)
        if not debug and value == ["http://localhost:3000"]:
            import warnings
            warnings.warn("CORS_ORIGINS is set to localhost in production! This will block real requests.")
        return value

    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def validate_secret_key(self) -> str:
        if not self.SECRET_KEY or self.SECRET_KEY == "change-this-to-a-random-secret-key-in-production":
            import warnings
            warnings.warn("SECRET_KEY is not set or is using the default value. Set a strong random secret in production.")
        return self.SECRET_KEY


settings = Settings()
