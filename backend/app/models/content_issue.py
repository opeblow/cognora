import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from app.database.base import Base


class ContentIssue(Base):
    __tablename__ = "content_issues"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content_type = Column(String(20), nullable=False)
    content_id = Column(String, nullable=False)
    section_index = Column(Integer, nullable=True)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="open")
    ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
