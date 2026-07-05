import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database.base import Base


class TextbookSection(Base):
    __tablename__ = "textbook_sections"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    topic_id = Column(String, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=True)
    section_index = Column(Integer, nullable=False)
    word_count = Column(Integer, nullable=True)
    is_generated = Column(Boolean, nullable=False, default=False)
    generated_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    topic = relationship("Topic", back_populates="textbook_sections")
