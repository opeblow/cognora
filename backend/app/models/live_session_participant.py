import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database.base import Base


class LiveSessionParticipant(Base):
    __tablename__ = "live_session_participants"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("live_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(10), nullable=False, default="audience")
    joined_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    left_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("LiveSession", back_populates="participants")
    user = relationship("User")
