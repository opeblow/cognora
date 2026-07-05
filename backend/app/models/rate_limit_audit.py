import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from app.database.base import Base


class RateLimitAudit(Base):
    __tablename__ = "rate_limit_audit"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True, index=True)
    ip_address = Column(String(45), nullable=False)
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    status_code = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
