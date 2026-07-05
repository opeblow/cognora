from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GamificationProfileResponse(BaseModel):
    total_xp: int
    level: int
    current_streak: int
    longest_streak: int
    streak_freezes: int
    next_level_xp: int
    xp_to_next_level: int


class BadgeResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    awarded_at: Optional[datetime] = None


class LeaderboardEntryResponse(BaseModel):
    user_id: str
    full_name: str
    avatar_url: Optional[str] = None
    total_xp: int
    level: int
    rank: int


class LeaderboardResponse(BaseModel):
    entries: list[LeaderboardEntryResponse]
    total_count: int
