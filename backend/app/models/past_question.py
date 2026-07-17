import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, JSON
from app.database.base import Base


class PastQuestion(Base):
    __tablename__ = "past_questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_board = Column(String(50), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    subject = Column(String(255), nullable=False, index=True)
    session = Column(String(100), nullable=True)
    questions = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
