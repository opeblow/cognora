from sqlalchemy.orm import Session
from app.models.user_settings import UserSettings
from app.models.user import User
from typing import Optional


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_settings(self, user_id: str) -> dict:
        settings = self.db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()

        if not settings:
            settings = UserSettings(user_id=user_id)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)

        return {
            "notifications": {
                "study_reminder_enabled": settings.study_reminder_enabled,
                "study_reminder_time": settings.study_reminder_time,
                "quiz_reminder_enabled": settings.quiz_reminder_enabled,
                "email_notifications": settings.email_notifications,
            },
            "academic": {
                "exam_focus": settings.exam_focus,
                "preferred_subjects": settings.preferred_subjects or [],
                "difficulty_preference": settings.difficulty_preference,
            },
            "preferences": {
                "timezone": settings.timezone,
            },
        }

    def update_notifications(
        self,
        user_id: str,
        study_reminder_enabled: Optional[bool] = None,
        study_reminder_time: Optional[str] = None,
        quiz_reminder_enabled: Optional[bool] = None,
        email_notifications: Optional[bool] = None,
    ) -> dict:
        settings = self._get_or_create(user_id)

        if study_reminder_enabled is not None:
            settings.study_reminder_enabled = study_reminder_enabled
        if study_reminder_time is not None:
            settings.study_reminder_time = study_reminder_time
        if quiz_reminder_enabled is not None:
            settings.quiz_reminder_enabled = quiz_reminder_enabled
        if email_notifications is not None:
            settings.email_notifications = email_notifications

        self.db.commit()
        return self.get_settings(user_id)

    def update_academic_preferences(
        self,
        user_id: str,
        exam_focus: Optional[str] = None,
        preferred_subjects: Optional[list[str]] = None,
        difficulty_preference: Optional[str] = None,
    ) -> dict:
        settings = self._get_or_create(user_id)

        if exam_focus is not None:
            settings.exam_focus = exam_focus
        if preferred_subjects is not None:
            settings.preferred_subjects = preferred_subjects
        if difficulty_preference is not None:
            settings.difficulty_preference = difficulty_preference

        self.db.commit()
        return self.get_settings(user_id)

    def update_preferences(
        self,
        user_id: str,
        timezone: Optional[str] = None,
    ) -> dict:
        settings = self._get_or_create(user_id)

        if timezone is not None:
            settings.timezone = timezone

        self.db.commit()
        return self.get_settings(user_id)

    def change_password(self, user_id: str, current_password: str, new_password: str) -> dict:
        from app.core.security import verify_password, hash_password

        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        if not user.password_hash:
            raise ValueError("Cannot change password for OAuth accounts")

        if not verify_password(current_password, user.password_hash):
            raise ValueError("Current password is incorrect")

        if len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters")

        user.password_hash = hash_password(new_password)
        self.db.commit()

        return {"message": "Password updated successfully"}

    def _get_or_create(self, user_id: str) -> UserSettings:
        settings = self.db.query(UserSettings).filter(
            UserSettings.user_id == user_id
        ).first()

        if not settings:
            settings = UserSettings(user_id=user_id)
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)

        return settings
