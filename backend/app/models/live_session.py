import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class LiveSession(Base):
    __tablename__ = "live_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id = Column(String(255), unique=True, nullable=False, index=True)
    tutor_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    subject = Column(String(255), nullable=False)
    topic = Column(String(255), nullable=True)
    status = Column(String(50), default="pending")
    provider = Column(String(50), default="mock")
    provider_room_id = Column(String(500), nullable=True)
    recording_url = Column(String(1000), nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    tutor = relationship("User", foreign_keys=[tutor_id], back_populates="tutoring_sessions")
    student = relationship("User", foreign_keys=[student_id], back_populates="learning_sessions")
    participants = relationship("LiveSessionParticipant", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("ClassroomMessage", back_populates="session", cascade="all, delete-orphan")
