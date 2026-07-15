import asyncio
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from app.database.base import get_db, SessionLocal
from app.database.redis import get_redis, NullRedis
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.lobby_service import StudyLobbyService
from app.schemas.lobby import (
    CreateLobbyRequest,
    LobbyResponse,
    LobbyListResponse,
    LobbyMessageResponse,
    LobbyHistoryResponse,
)
from app.core.security import decode_token

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/lobbies", tags=["Study Lobbies"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self._pubsub_task: asyncio.Task | None = None
        self._started = False

    async def _ensure_pubsub(self):
        if self._started:
            return
        self._started = True
        redis = await get_redis()
        if isinstance(redis, NullRedis):
            logger.info("Redis unavailable — lobby broadcasts are single-server only")
            return
        self._pubsub_task = asyncio.create_task(self._listen_redis(redis))

    async def _listen_redis(self, redis):
        pubsub = redis.pubsub()
        await pubsub.psubscribe("lobby:*")
        try:
            while True:
                msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if msg and msg["type"] == "pmessage":
                    channel = msg["channel"]
                    lobby_id = channel.split(":", 1)[1]
                    data = json.loads(msg["data"])
                    await self._deliver_local(lobby_id, data)
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Redis pubsub listener error: {e}")
        finally:
            try:
                await pubsub.close()
            except Exception:
                pass

    async def _deliver_local(self, lobby_id: str, message: dict):
        if lobby_id not in self.active_connections:
            return
        dead = []
        for ws in self.active_connections[lobby_id]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(lobby_id, ws)

    async def connect(self, lobby_id: str, websocket: WebSocket):
        if lobby_id not in self.active_connections:
            self.active_connections[lobby_id] = []
        self.active_connections[lobby_id].append(websocket)

    def disconnect(self, lobby_id: str, websocket: WebSocket):
        if lobby_id in self.active_connections:
            try:
                self.active_connections[lobby_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[lobby_id]:
                del self.active_connections[lobby_id]

    async def broadcast(self, lobby_id: str, message: dict, exclude: WebSocket = None):
        await self._ensure_pubsub()

        redis = await get_redis()
        if not isinstance(redis, NullRedis):
            await redis.publish(f"lobby:{lobby_id}", json.dumps(message))
            return

        await self._deliver_local(lobby_id, message)


manager = ConnectionManager()


@router.post("", response_model=LobbyResponse)
def create_lobby(
    request: CreateLobbyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyLobbyService(db)
    lobby = service.create_lobby(
        name=request.name,
        created_by=str(current_user.id),
        subject=request.subject,
        topic=request.topic,
        max_participants=request.max_participants,
    )
    return LobbyResponse(
        id=lobby.id,
        name=lobby.name,
        subject=lobby.subject,
        topic=lobby.topic,
        created_by=lobby.created_by,
        max_participants=lobby.max_participants,
        is_active=lobby.is_active,
        created_at=lobby.created_at,
    )


@router.get("", response_model=LobbyListResponse)
def list_lobbies(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyLobbyService(db)
    lobbies, total = service.get_active_lobbies(skip, limit)
    return LobbyListResponse(
        lobbies=[
            LobbyResponse(
                id=l.id,
                name=l.name,
                subject=l.subject,
                topic=l.topic,
                created_by=l.created_by,
                max_participants=l.max_participants,
                is_active=l.is_active,
                created_at=l.created_at,
            )
            for l in lobbies
        ],
        total=total,
    )


@router.get("/{lobby_id}", response_model=LobbyResponse)
def get_lobby(
    lobby_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyLobbyService(db)
    lobby = service.get_lobby(lobby_id)
    if not lobby:
        raise HTTPException(status_code=404, detail="Lobby not found")
    return LobbyResponse(
        id=lobby.id,
        name=lobby.name,
        subject=lobby.subject,
        topic=lobby.topic,
        created_by=lobby.created_by,
        max_participants=lobby.max_participants,
        is_active=lobby.is_active,
        created_at=lobby.created_at,
    )


@router.get("/{lobby_id}/history", response_model=LobbyHistoryResponse)
def get_lobby_history(
    lobby_id: str,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyLobbyService(db)
    messages = service.get_history(lobby_id, limit)
    return LobbyHistoryResponse(
        messages=[
            LobbyMessageResponse(
                id=m.id,
                lobby_id=m.lobby_id,
                user_id=m.user_id,
                username=m.username,
                content=m.content,
                is_ai_response=m.is_ai_response,
                created_at=m.created_at,
            )
            for m in messages
        ]
    )


@router.post("/{lobby_id}/close", response_model=dict)
def close_lobby(
    lobby_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyLobbyService(db)
    lobby = service.close_lobby(lobby_id, str(current_user.id))
    if not lobby:
        raise HTTPException(status_code=404, detail="Lobby not found or not your lobby")
    return {"message": "Lobby closed", "lobby_id": lobby_id}


@router.websocket("/{lobby_id}/ws")
async def lobby_websocket(websocket: WebSocket, lobby_id: str):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        metadata = json.loads(data)
    except Exception:
        await websocket.send_json({"error": "Invalid connection metadata"})
        await websocket.close()
        return

    token = metadata.get("token", "")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.send_json({"error": "Authentication required"})
        await websocket.close()
        return

    user_id = payload.get("sub")
    db = SessionLocal()
    try:
        from app.models.user import User as UserModel
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user or not user.is_active:
            await websocket.send_json({"error": "User not found or inactive"})
            await websocket.close()
            return

        username = user.full_name or user.email.split("@")[0]

        service = StudyLobbyService(db)
        lobby = service.get_lobby(lobby_id)
        if not lobby or not lobby.is_active:
            await websocket.send_json({"error": "Lobby not found or inactive"})
            await websocket.close()
            return

        await manager.connect(lobby_id, websocket)

        join_msg = f"{username} joined the lobby"
        member = service.save_message(lobby_id, user_id, "System", join_msg)
        await manager.broadcast(lobby_id, {
            "type": "message",
            "id": member.id,
            "username": "System",
            "content": join_msg,
            "is_ai_response": False,
            "created_at": member.created_at.isoformat(),
        })

        msg_buffer = []

        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            content = data.get("content", "").strip()
            if not content:
                continue

            msg = service.save_message(lobby_id, user_id, username, content)
            msg_buffer.append({
                "username": username,
                "content": content,
            })

            await manager.broadcast(lobby_id, {
                "type": "message",
                "id": msg.id,
                "username": username,
                "content": content,
                "is_ai_response": False,
                "created_at": msg.created_at.isoformat(),
            })

            if len(msg_buffer) >= 3:
                try:
                    ai_text = await asyncio.to_thread(service.generate_ai_response, lobby, msg_buffer)
                    if ai_text:
                        ai_msg = service.save_message(
                            lobby_id, None, "Cognora AI", ai_text, is_ai_response=True
                        )
                        await manager.broadcast(lobby_id, {
                            "type": "message",
                            "id": ai_msg.id,
                            "username": "Cognora AI",
                            "content": ai_text,
                            "is_ai_response": True,
                            "created_at": ai_msg.created_at.isoformat(),
                        })
                except Exception as e:
                    logger.error(f"AI moderator error: {e}")
                msg_buffer = []

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected from lobby {lobby_id}")
        manager.disconnect(lobby_id, websocket)
        if 'username' in locals() and 'service' in locals():
            leave_msg = f"{username} left the lobby"
            try:
                member = service.save_message(lobby_id, user_id, "System", leave_msg)
                await manager.broadcast(lobby_id, {
                    "type": "message",
                    "id": member.id,
                    "username": "System",
                    "content": leave_msg,
                    "is_ai_response": False,
                    "created_at": member.created_at.isoformat(),
                })
            except Exception:
                pass
    except Exception as e:
        logger.error(f"WebSocket error in lobby {lobby_id}: {e}")
        manager.disconnect(lobby_id, websocket)
    finally:
        db.close()
