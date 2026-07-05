import uuid
import logging
import secrets
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.live_session import LiveSession

logger = logging.getLogger(__name__)


class LiveSessionService:
    def __init__(self, db: Session):
        self.db = db
        self.provider = settings.LIVE_SESSION_PROVIDER

    def create_room(
        self,
        tutor_id: str,
        subject: str,
        topic: str | None = None,
        student_id: str | None = None,
    ) -> dict:
        room_id = f"room_{uuid.uuid4().hex[:12]}"

        provider_room_id = None
        token = None

        if self.provider == "mock":
            provider_room_id = room_id
            token = secrets.token_urlsafe(32)
        elif self.provider == "agora":
            try:
                from app.services.agora_service import AgoraService
                agora = AgoraService()
                channel = agora.create_channel(subject, topic)
                provider_room_id = channel["channel_name"]
                token = channel["token"]
            except Exception as e:
                logger.error(f"Agora room creation failed: {e}")
                provider_room_id = room_id
                token = secrets.token_urlsafe(32)
        elif self.provider == "hundred_ms":
            provider_room_id, token = self._create_provider_room(room_id)

        session = LiveSession(
            room_id=room_id,
            tutor_id=tutor_id,
            student_id=student_id,
            subject=subject,
            topic=topic,
            status="pending",
            provider=self.provider,
            provider_room_id=provider_room_id,
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)

        return {
            "room_id": room_id,
            "provider": self.provider,
            "provider_room_id": provider_room_id,
            "token": token,
            "status": session.status,
            "created_at": session.created_at,
        }

    def start_session(self, room_id: str, tutor_id: str) -> LiveSession | None:
        session = self.db.query(LiveSession).filter(
            LiveSession.room_id == room_id,
            LiveSession.tutor_id == tutor_id,
        ).first()

        if not session:
            return None

        session.status = "active"
        session.started_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(session)
        return session

    def end_session(
        self, room_id: str, tutor_id: str, recording_url: str | None = None
    ) -> LiveSession | None:
        session = self.db.query(LiveSession).filter(
            LiveSession.room_id == room_id,
            LiveSession.tutor_id == tutor_id,
        ).first()

        if not session:
            return None

        session.status = "completed"
        session.ended_at = datetime.now(timezone.utc)
        if recording_url:
            session.recording_url = recording_url
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, room_id: str) -> LiveSession | None:
        return self.db.query(LiveSession).filter(
            LiveSession.room_id == room_id
        ).first()

    def get_user_sessions(
        self, user_id: str, role: str = "tutor", skip: int = 0, limit: int = 50
    ):
        if role == "tutor":
            query = self.db.query(LiveSession).filter(
                LiveSession.tutor_id == user_id
            )
        else:
            query = self.db.query(LiveSession).filter(
                LiveSession.student_id == user_id
            )

        query = query.order_by(LiveSession.created_at.desc())
        total = query.count()
        sessions = query.offset(skip).limit(limit).all()
        return sessions, total

    def _create_provider_room(self, room_id: str) -> tuple[str, str]:
        logger.warning(
            f"Provider '{self.provider}' not fully configured. "
            f"Set HUNDREDMS_API_KEY or AGORA_APP_ID in .env"
        )
        return room_id, secrets.token_urlsafe(32)
