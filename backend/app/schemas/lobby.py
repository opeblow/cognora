from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CreateLobbyRequest(BaseModel):
    name: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    max_participants: int = 10


class LobbyResponse(BaseModel):
    id: str
    name: str
    subject: Optional[str] = None
    topic: Optional[str] = None
    created_by: str
    max_participants: int
    is_active: bool
    created_at: datetime


class LobbyListResponse(BaseModel):
    lobbies: list[LobbyResponse]
    total: int


class LobbyMessageResponse(BaseModel):
    id: str
    lobby_id: str
    user_id: Optional[str] = None
    username: Optional[str] = None
    content: str
    is_ai_response: bool
    created_at: datetime


class LobbyHistoryResponse(BaseModel):
    messages: list[LobbyMessageResponse]
