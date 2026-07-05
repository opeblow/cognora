import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base


class StudyLobby(Base):
    __tablename__ = "study_lobbies"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=True)
    topic = Column(String(255), nullable=True)
    created_by = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    max_participants = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    creator = relationship("User", back_populates="created_lobbies")
    messages = relationship("LobbyMessage", back_populates="lobby", cascade="all, delete-orphan")


class LobbyMessage(Base):
    __tablename__ = "lobby_messages"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lobby_id = Column(String, ForeignKey("study_lobbies.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    username = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    is_ai_response = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    lobby = relationship("StudyLobby", back_populates="messages")
    user = relationship("User")
