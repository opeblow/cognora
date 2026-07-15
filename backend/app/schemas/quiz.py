from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class QuizResponse(BaseModel):
    id: str
    subject_id: str
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit_minutes: Optional[str] = None
    pass_percentage: Optional[str] = None
    subject: Optional[dict] = None


class QuizListResponse(BaseModel):
    quizzes: list[QuizResponse]
    total: int


class QuestionResponse(BaseModel):
    id: str
    text: str
    options: list
    order_index: Optional[str] = None
    question_type: str


class QuizDetailResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit_minutes: Optional[str] = None
    pass_percentage: Optional[str] = None
    questions: list[QuestionResponse]
    session_id: str
    question_count: int
    subject: Optional[dict] = None


class SubmitQuizRequest(BaseModel):
    session_id: str
    answers: dict
    time_taken_seconds: int


class SubmitQuizResponse(BaseModel):
    score: int
    total: int
    percentage: float
    passed: bool
    answers: list[dict]


class QuizAttemptResponse(BaseModel):
    id: str
    quiz_id: str
    score: Optional[str] = None
    total: Optional[str] = None
    percentage: Optional[str] = None
    time_taken_seconds: Optional[str] = None
    completed_at: Optional[datetime] = None
    quiz: Optional[QuizResponse] = None


class QuizAttemptListResponse(BaseModel):
    attempts: list[QuizAttemptResponse]
    total: int
