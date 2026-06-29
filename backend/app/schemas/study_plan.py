from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime


class StudyPlanDayResponse(BaseModel):
    id: str
    date: date
    subjects: Optional[list] = None
    topics: Optional[list] = None
    duration_minutes: Optional[str] = None
    is_completed: str
    notes: Optional[str] = None

    


class StudyPlanResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    plan_type: str
    start_date: date
    end_date: Optional[date] = None
    is_active: str
    days: list[StudyPlanDayResponse] = []

    


class StudyPlanListResponse(BaseModel):
    plans: list[StudyPlanResponse]
    total: int


class CreateStudyPlanRequest(BaseModel):
    title: str
    description: Optional[str] = None
    plan_type: str
    start_date: date
    end_date: Optional[date] = None
    subjects: list[str]

