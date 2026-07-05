import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class Chapter(Base):
    __tablename__ = "chapters"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    estimated_minutes = Column(Integer, nullable=True)
    is_published = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    subject = relationship("Subject", back_populates="chapters")
    lessons = relationship("Lesson", back_populates="chapter", cascade="all, delete-orphan")
