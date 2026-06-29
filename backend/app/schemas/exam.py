from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ExamResponse(BaseModel):
    id: str
    subject_id: str
    title: str
    description: Optional[str] = None
    exam_type: str
    year: Optional[str] = None
    time_limit_minutes: Optional[str] = None
    total_questions: Optional[str] = None
    pass_percentage: Optional[str] = None
    subject: Optional[dict] = None

    


class ExamListResponse(BaseModel):
    exams: list[ExamResponse]
    total: int


class ExamDetailResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    exam_type: str
    year: Optional[str] = None
    time_limit_minutes: Optional[str] = None
    pass_percentage: Optional[str] = None
    questions: list[dict]
    subject: Optional[dict] = None


class StartExamResponse(BaseModel):
    result_id: str
    exam: ExamDetailResponse
    time_limit_minutes: int


class SubmitExamRequest(BaseModel):
    answers: dict
    time_taken_seconds: int


class SubmitExamResponse(BaseModel):
    score: int
    total: int
    percentage: float
    passed: bool
    status: str
    answers: list[dict]


class ExamResultResponse(BaseModel):
    id: str
    exam_id: str
    score: Optional[str] = None
    total: Optional[str] = None
    percentage: Optional[str] = None
    time_taken_seconds: Optional[str] = None
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    exam: Optional[ExamResponse] = None

    


class ExamResultListResponse(BaseModel):
    results: list[ExamResultResponse]
    total: int

