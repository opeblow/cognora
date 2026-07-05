from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.services.study_plan_service import StudyPlanService
from app.models.user import User
from pydantic import BaseModel
from typing import Optional
from datetime import date

router = APIRouter(prefix="/study-planner", tags=["Study Planner"])


class CreatePlanRequest(BaseModel):
    title: str
    description: Optional[str] = None
    plan_type: str
    start_date: date
    end_date: Optional[date] = None
    subjects: list[str]
    use_ai: bool = False


class MarkDayRequest(BaseModel):
    day_id: str


@router.get("", response_model=dict)
def get_plans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyPlanService(db)
    return service.get_plans(str(current_user.id))


@router.get("/today", response_model=dict)
def get_today_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyPlanService(db)
    return service.get_today_tasks(str(current_user.id))


@router.get("/calendar", response_model=dict)
def get_weekly_calendar(
    week_start: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyPlanService(db)
    return service.get_weekly_calendar(str(current_user.id), week_start)


@router.get("/{plan_id}", response_model=dict)
def get_plan(
    plan_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyPlanService(db)
    try:
        return service.get_plan(plan_id, str(current_user.id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("", response_model=dict)
def create_plan(
    request: CreatePlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyPlanService(db)
    try:
        return service.create_plan(
            user_id=str(current_user.id),
            title=request.title,
            description=request.description,
            plan_type=request.plan_type,
            start_date=request.start_date,
            end_date=request.end_date,
            subjects=request.subjects,
            use_ai=request.use_ai,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/days/{day_id}/complete", response_model=dict)
def mark_day_completed(
    day_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = StudyPlanService(db)
    try:
        result = service.mark_day_completed(day_id, str(current_user.id))
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
