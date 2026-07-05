import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base


class ClassroomMessage(Base):
    __tablename__ = "classroom_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("live_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_type = Column(String(20), nullable=False, default="chat")
    payload = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))

    session = relationship("LiveSession", back_populates="messages")
    user = relationship("User")
