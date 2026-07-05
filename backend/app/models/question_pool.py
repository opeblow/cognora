import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from app.database.base import Base


class QuestionPool(Base):
    __tablename__ = "question_pool"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    topic = Column(String(255), nullable=True, index=True)
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(50), default="medium")
    question_type = Column(String(50), default="multiple_choice")
    times_used = Column(Integer, default=0)
    source = Column(String(50), default="ai_generated")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    subject = relationship("Subject", backref="question_pool")


class UserSeenQuestion(Base):
    __tablename__ = "user_seen_questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String, ForeignKey("question_pool.id", ondelete="CASCADE"), nullable=False, index=True)
    __table_args__ = (Index("ix_user_question", "user_id", "question_id", unique=True),)
    seen_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", backref="seen_questions")
    question = relationship("QuestionPool", backref="seen_by")
