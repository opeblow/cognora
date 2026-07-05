import json
import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.lobby import StudyLobby, LobbyMessage
from app.models.user import User
from app.core.config import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


class StudyLobbyService:
    def __init__(self, db: Session):
        self.db = db
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY, timeout=30.0) if settings.OPENAI_API_KEY else None

    def create_lobby(
        self, name: str, created_by: str,
        subject: Optional[str] = None, topic: Optional[str] = None,
        max_participants: int = 10,
    ) -> StudyLobby:
        lobby = StudyLobby(
            name=name,
            subject=subject,
            topic=topic,
            created_by=created_by,
            max_participants=max_participants,
            is_active=True,
        )
        self.db.add(lobby)
        self.db.commit()
        self.db.refresh(lobby)
        return lobby

    def get_lobby(self, lobby_id: str) -> Optional[StudyLobby]:
        return self.db.query(StudyLobby).filter(StudyLobby.id == lobby_id).first()

    def get_active_lobbies(self, skip: int = 0, limit: int = 50) -> tuple[list[StudyLobby], int]:
        query = self.db.query(StudyLobby).filter(
            StudyLobby.is_active == True
        ).order_by(StudyLobby.created_at.desc())
        total = query.count()
        lobbies = query.offset(skip).limit(limit).all()
        return lobbies, total

    def save_message(
        self, lobby_id: str, user_id: Optional[str],
        username: Optional[str], content: str,
        is_ai_response: bool = False,
    ) -> LobbyMessage:
        msg = LobbyMessage(
            lobby_id=lobby_id,
            user_id=user_id,
            username=username,
            content=content,
            is_ai_response=is_ai_response,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_history(self, lobby_id: str, limit: int = 100) -> list[LobbyMessage]:
        return (
            self.db.query(LobbyMessage)
            .filter(LobbyMessage.lobby_id == lobby_id)
            .order_by(LobbyMessage.created_at.asc())
            .limit(limit)
            .all()
        )

    def generate_ai_response(self, lobby: StudyLobby, recent_messages: list[dict]) -> Optional[str]:
        if not self.openai:
            logger.warning("OpenAI not configured, skipping AI moderation")
            return None

        context = f"Study Lobby: {lobby.name}\nSubject: {lobby.subject or 'General'}\nTopic: {lobby.topic or 'General'}\n\n"

        chat_log = "\n".join(
            f"{m.get('username', 'Student')}: {m.get('content', '')}"
            for m in recent_messages[-20:]
        )

        system_prompt = (
            "You are Cognora AI, a tutor-moderator for a student study lobby. "
            "Your role is to:\n"
            "1. Monitor the conversation for questions or confusion.\n"
            "2. If students are stuck on a concept, provide a helpful hint or explanation.\n"
            "3. If the conversation goes off-topic, gently redirect it back to studying.\n"
            "4. Keep responses concise (1-3 sentences) and encouraging.\n"
            "5. Only intervene when genuinely helpful — do not spam.\n\n"
            "Respond ONLY if you have something useful to add. Otherwise respond with 'NO_INTERVENTION'."
        )

        prompt = (
            f"{context}"
            f"Recent conversation:\n{chat_log}\n\n"
            f"Should the AI moderator intervene? If yes, provide a short helpful response. "
            f"If not, respond with exactly: NO_INTERVENTION"
        )

        try:
            response = self.openai.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=300,
            )
            text = response.choices[0].message.content or "NO_INTERVENTION"
            text = text.strip()

            if text == "NO_INTERVENTION" or not text:
                return None

            return text
        except Exception as e:
            logger.error(f"AI moderator failed: {e}")
            return None

    def close_lobby(self, lobby_id: str, user_id: str) -> Optional[StudyLobby]:
        lobby = self.db.query(StudyLobby).filter(
            StudyLobby.id == lobby_id,
            StudyLobby.created_by == user_id,
        ).first()
        if not lobby:
            return None
        lobby.is_active = False
        self.db.commit()
        self.db.refresh(lobby)
        return lobby
