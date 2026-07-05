import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class AudioRecording(Base):
    __tablename__ = "audio_recordings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(1000), nullable=False)
    mime_type = Column(String(100), nullable=False)
    duration_seconds = Column(Float, nullable=True)
    transcript = Column(Text, nullable=True)
    ai_feedback = Column(Text, nullable=True)
    processing_status = Column(String(50), default="pending")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="audio_recordings")
