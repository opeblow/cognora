import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, JSON
from app.database.base import Base


class Syllabus(Base):
    __tablename__ = "syllabi"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_board = Column(String(20), nullable=False)
    subject = Column(String(200), nullable=False)
    year = Column(String(4), nullable=False)
    syllabus_data = Column(JSON, nullable=False)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "exam_board": self.exam_board,
            "subject": self.subject,
            "year": self.year,
            "syllabus_data": self.syllabus_data,
            "source_url": self.source_url,
        }
