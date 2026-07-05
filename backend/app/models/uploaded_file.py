import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String(500), nullable=False)
    stored_filename = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    storage_path = Column(String(1000), nullable=False)
    storage_backend = Column(String(50), default="local")
    ocr_text = Column(Text, nullable=True)
    ocr_status = Column(String(50), default="pending")
    ocr_processed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="uploaded_files")
