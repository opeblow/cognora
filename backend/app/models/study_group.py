import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class StudyGroup(Base):
    __tablename__ = "study_groups"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(255), nullable=True)
    creator_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    max_members = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    creator = relationship("User", back_populates="created_study_groups")
    members = relationship("StudyGroupMember", back_populates="group", cascade="all, delete-orphan")
    messages = relationship("StudyGroupMessage", back_populates="group", cascade="all, delete-orphan")


class StudyGroupMember(Base):
    __tablename__ = "study_group_members"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False, default="member")
    joined_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    group = relationship("StudyGroup", back_populates="members")
    user = relationship("User", back_populates="study_group_memberships")


class StudyGroupMessage(Base):
    __tablename__ = "study_group_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = Column(String, ForeignKey("study_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    group = relationship("StudyGroup", back_populates="messages")
    user = relationship("User")
