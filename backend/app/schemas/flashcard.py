from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class FlashcardResponse(BaseModel):
    id: str
    question: str
    answer: str
    difficulty: Optional[str] = None
    tags: Optional[str] = None
    topic_id: Optional[str] = None
    section_index: Optional[int] = None
    next_review_at: Optional[datetime] = None
    ease_factor: float = 2.5
    interval_days: int = 0
    repetitions: int = 0


class FlashcardListResponse(BaseModel):
    flashcards: list[FlashcardResponse]
    total: int


class ReviewFlashcardRequest(BaseModel):
    quality: int


class ReviewFlashcardResponse(BaseModel):
    id: str
    next_review_at: Optional[datetime] = None
    interval_days: int
    ease_factor: float
    repetitions: int


class GenerateFlashcardsRequest(BaseModel):
    topic_id: str
    count: int = 10
