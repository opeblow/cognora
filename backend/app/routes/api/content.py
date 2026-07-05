from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.content_storage import ContentStorage
from app.services.syllabus_service import SyllabusService
from app.services.curriculum_service import CurriculumPipeline
from app.core.errors import AppError
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/content", tags=["Content"])


class ProgressUpdateRequest(BaseModel):
    sections_read: Optional[list[int]] = None
    exercises_attempted: Optional[int] = None
    exercises_passed: Optional[int] = None
    deep_dives_completed: Optional[list[str]] = None
    last_position: Optional[str] = None
    time_spent_seconds: Optional[int] = None


@router.get("/topics/{topic_id}")
async def get_topic_content(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    storage = ContentStorage(db)
    try:
        return await storage.get_topic_content(topic_id)
    except AppError as e:
        raise HTTPException(status_code=e.status, detail=e.message)


@router.get("/topics/{topic_id}/progress")
async def get_topic_progress(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    storage = ContentStorage(db)
    return await storage.get_topic_progress(str(current_user.id), topic_id)


@router.patch("/topics/{topic_id}/progress")
async def update_topic_progress(
    topic_id: str,
    update: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    storage = ContentStorage(db)
    await storage.update_topic_progress(
        str(current_user.id),
        topic_id,
        {k: v for k, v in update.model_dump().items() if v is not None},
    )
    return await storage.get_topic_progress(str(current_user.id), topic_id)


@router.get("/syllabus/{exam_board}/{subject}")
async def get_syllabus(
    exam_board: str,
    subject: str,
    current_user: User = Depends(get_current_user),
):
    service = SyllabusService()
    syllabus = await service.get_syllabus(exam_board, subject)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    return syllabus


@router.get("/topics/{topic_id}/alignment")
async def check_alignment(
    topic_id: str,
    exam_board: str = "WAEC",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    storage = ContentStorage(db)
    topic = await storage.get_topic_content(topic_id)
    service = SyllabusService()
    result = await service.verify_alignment(
        topic.get("html_content", ""), exam_board, "General", topic.get("title", "")
    )
    return result


@router.post("/generate/subject")
async def generate_subject(
    subject: str,
    exam_board: str = "WAEC",
    current_user: User = Depends(get_current_user),
):
    pipeline = CurriculumPipeline()
    subject_id = await pipeline.generate_full_subject(subject, exam_board)
    return {"subject_id": subject_id, "status": "generation_started"}
