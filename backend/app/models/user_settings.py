import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    study_reminder_enabled = Column(Boolean, default=True)
    study_reminder_time = Column(String(5), default="09:00")
    quiz_reminder_enabled = Column(Boolean, default=True)
    email_notifications = Column(Boolean, default=True)

    exam_focus = Column(String(50), default="JAMB")
    preferred_subjects = Column(JSON, default=list)
    difficulty_preference = Column(String(20), default="medium")

    timezone = Column(String(50), default="Africa/Lagos")

    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="settings")
