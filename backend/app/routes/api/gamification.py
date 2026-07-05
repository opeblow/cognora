from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.gamification_service import GamificationService
from app.schemas.gamification import (
    GamificationProfileResponse,
    BadgeResponse,
    LeaderboardResponse,
    LeaderboardEntryResponse,
)

router = APIRouter(prefix="/gamification", tags=["Gamification"])


@router.get("/profile", response_model=GamificationProfileResponse)
def get_gamification_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = GamificationService(db)
    return service.get_profile(current_user)


@router.get("/badges", response_model=list[BadgeResponse])
def get_user_badges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = GamificationService(db)
    return service.get_badges(str(current_user.id))


@router.get("/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    service = GamificationService(db)
    entries, total = service.get_leaderboard(limit)
    return LeaderboardResponse(
        entries=[
            LeaderboardEntryResponse(**e) for e in entries
        ],
        total_count=total,
    )
