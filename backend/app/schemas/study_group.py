from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CreateGroupRequest(BaseModel):
    name: str
    subject: Optional[str] = None
    description: Optional[str] = None
    max_members: int = 10


class StudyGroupMemberResponse(BaseModel):
    id: str
    user_id: str
    role: str
    joined_at: datetime
    full_name: Optional[str] = None


class StudyGroupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    subject: Optional[str] = None
    creator_id: str
    max_members: int
    is_active: bool
    created_at: datetime
    member_count: int = 0
    creator_name: Optional[str] = None


class StudyGroupDetailResponse(StudyGroupResponse):
    members: list[StudyGroupMemberResponse] = []


class StudyGroupListResponse(BaseModel):
    groups: list[StudyGroupResponse]
    total: int


class SendMessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: str
    group_id: str
    user_id: str
    content: str
    created_at: datetime
    full_name: Optional[str] = None


class MessagesResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
