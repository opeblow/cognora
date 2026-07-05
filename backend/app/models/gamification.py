import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base


class Badge(Base):
    __tablename__ = "badges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon = Column(String(500), nullable=True)
    criteria_type = Column(String(100), nullable=False)
    criteria_value = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class UserBadge(Base):
    __tablename__ = "user_badges"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = Column(String, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    awarded_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="badges")
    badge = relationship("Badge")
