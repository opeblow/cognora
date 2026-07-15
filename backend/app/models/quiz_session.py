import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    questions_data = Column(JSON, nullable=False)
    score = Column(Integer, nullable=True)
    total = Column(Integer, nullable=True)
    percentage = Column(Integer, nullable=True)
    time_taken_seconds = Column(Integer, nullable=True)
    status = Column(String(50), default="in_progress")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    quiz = relationship("Quiz", backref="sessions")
    user = relationship("User", backref="quiz_sessions")
