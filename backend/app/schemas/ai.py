from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class TutorRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000)
    subject: Optional[str] = None
    context: Optional[list[dict]] = None


class TutorResponse(BaseModel):
    response: str
    suggestions: list[str] = []


class GenerateQuizRequest(BaseModel):
    subject: str
    topic: str
    difficulty: str = "medium"
    num_questions: int = Field(default=5, ge=1, le=20)


class GenerateQuizResponse(BaseModel):
    questions: list[dict]
    title: str

