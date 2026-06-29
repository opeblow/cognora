import uuid
from datetime import datetime, timezone, date
from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, JSON
from sqlalchemy import String
from sqlalchemy.orm import relationship
from app.database.base import Base


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    plan_type = Column(String(50), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(String(50), default="true")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="study_plans")
    days = relationship("StudyPlanDay", back_populates="study_plan", cascade="all, delete-orphan")


class StudyPlanDay(Base):
    __tablename__ = "study_plan_days"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    study_plan_id = Column(String, ForeignKey("study_plans.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    subjects = Column(JSON, nullable=True)
    topics = Column(JSON, nullable=True)
    duration_minutes = Column(String(50), nullable=True)
    is_completed = Column(String(50), default="false")
    notes = Column(Text, nullable=True)

    study_plan = relationship("StudyPlan", back_populates="days")



