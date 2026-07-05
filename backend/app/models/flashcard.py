import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Text, DateTime, ForeignKey,
)
from sqlalchemy.orm import relationship
from app.database.base import Base


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="SET NULL"), nullable=True)
    topic_id = Column(String, ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    section_index = Column(Integer, nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    difficulty = Column(String(50), default="medium")
    tags = Column(Text, nullable=True)
    source = Column(String(100), default="ai_generated")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="flashcards")
    review = relationship("FlashcardReview", back_populates="flashcard", uselist=False, cascade="all, delete-orphan")


class FlashcardReview(Base):
    __tablename__ = "flashcard_reviews"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    flashcard_id = Column(String, ForeignKey("flashcards.id", ondelete="CASCADE"), nullable=False, unique=True)
    ease_factor = Column(Float, default=2.5)
    interval_days = Column(Integer, default=0)
    repetitions = Column(Integer, default=0)
    next_review_at = Column(DateTime(timezone=True), nullable=True)
    last_reviewed_at = Column(DateTime(timezone=True), nullable=True)

    flashcard = relationship("Flashcard", back_populates="review")
