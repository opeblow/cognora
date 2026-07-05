from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.services.settings_service import SettingsService
from app.models.user import User
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/settings", tags=["Settings"])


class UpdateNotificationsRequest(BaseModel):
    study_reminder_enabled: Optional[bool] = None
    study_reminder_time: Optional[str] = None
    quiz_reminder_enabled: Optional[bool] = None
    email_notifications: Optional[bool] = None


class UpdateAcademicRequest(BaseModel):
    exam_focus: Optional[str] = None
    preferred_subjects: Optional[list[str]] = None
    difficulty_preference: Optional[str] = None


class UpdatePreferencesRequest(BaseModel):
    timezone: Optional[str] = None


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.get("", response_model=dict)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = SettingsService(db)
    return service.get_settings(str(current_user.id))


@router.put("/notifications", response_model=dict)
def update_notifications(
    request: UpdateNotificationsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = SettingsService(db)
    return service.update_notifications(
        user_id=str(current_user.id),
        study_reminder_enabled=request.study_reminder_enabled,
        study_reminder_time=request.study_reminder_time,
        quiz_reminder_enabled=request.quiz_reminder_enabled,
        email_notifications=request.email_notifications,
    )


@router.put("/academic", response_model=dict)
def update_academic_preferences(
    request: UpdateAcademicRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = SettingsService(db)
    return service.update_academic_preferences(
        user_id=str(current_user.id),
        exam_focus=request.exam_focus,
        preferred_subjects=request.preferred_subjects,
        difficulty_preference=request.difficulty_preference,
    )


@router.put("/preferences", response_model=dict)
def update_preferences(
    request: UpdatePreferencesRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = SettingsService(db)
    return service.update_preferences(
        user_id=str(current_user.id),
        timezone=request.timezone,
    )


@router.post("/change-password", response_model=dict)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = SettingsService(db)
    try:
        return service.change_password(
            user_id=str(current_user.id),
            current_password=request.current_password,
            new_password=request.new_password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
