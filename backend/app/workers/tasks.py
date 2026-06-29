from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.workers.celery_app import celery_app
from app.database.base import SessionLocal, engine, Base
from app.repositories.user import UserRepository
from app.models.user import User
from app.core.config import settings


@celery_app.task
def reset_weekly_credits():
    db = SessionLocal()
    try:
        repo = UserRepository(db)
        users, _ = repo.get_all()
        now = datetime.now(timezone.utc)
        for user in users:
            if user.weekly_credits_reset_at and user.weekly_credits_reset_at <= now:
                user.weekly_credits_used = "0"
                user.weekly_credits_reset_at = now + timedelta(days=7)
        db.commit()
    finally:
        db.close()


@celery_app.task
def send_email(to: str, subject: str, body: str):
    from app.utils.email import EmailService
    service = EmailService()
    service.send_email(to, subject, body)


@celery_app.task
def cleanup_expired_tokens():
    db = SessionLocal()
    try:
        from app.models.user import EmailVerification, PasswordReset
        from sqlalchemy import delete

        now = datetime.now(timezone.utc)
        db.execute(
            delete(EmailVerification).where(EmailVerification.expires_at < now)
        )
        db.execute(
            delete(PasswordReset).where(PasswordReset.expires_at < now)
        )
        db.commit()
    finally:
        db.close()
