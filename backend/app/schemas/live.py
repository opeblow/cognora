from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CreateRoomRequest(BaseModel):
    subject: str
    topic: Optional[str] = None
    student_id: Optional[str] = None


class RoomResponse(BaseModel):
    room_id: str
    provider: str
    provider_room_id: Optional[str] = None
    token: Optional[str] = None
    status: str
    created_at: datetime


class EndSessionRequest(BaseModel):
    recording_url: Optional[str] = None


class SessionDetailResponse(BaseModel):
    id: str
    room_id: str
    subject: str
    topic: Optional[str] = None
    status: str
    provider: str
    recording_url: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
