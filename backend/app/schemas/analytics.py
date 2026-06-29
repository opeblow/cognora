from pydantic import BaseModel, ConfigDict
from typing import Optional


class SubjectStat(BaseModel):
    subject_id: str
    subject_name: str
    lessons_completed: int
    quizzes_taken: int
    average_score: float
    total_study_time_minutes: int


class AnalyticsResponse(BaseModel):
    strong_subjects: list[SubjectStat]
    weak_subjects: list[SubjectStat]
    total_quizzes_taken: int
    total_exams_taken: int
    overall_average: float
    learning_streak: int
    total_study_time_minutes: int


class PerformanceTrend(BaseModel):
    date: str
    quiz_score: Optional[float] = None
    exam_score: Optional[float] = None
    study_time_minutes: int


class DashboardResponse(BaseModel):
    welcome_name: str
    credits: int
    weekly_credits_remaining: int
    learning_streak: int
    recent_activity: list[dict]
    progress_overview: list[SubjectStat]
    subject_stats: list[SubjectStat]

