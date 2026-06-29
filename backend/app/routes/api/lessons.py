from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.repositories.subject import SubjectRepository
from app.repositories.lesson import LessonRepository
from app.models.user import User

router = APIRouter(prefix="/subjects", tags=["Lessons"])


@router.get("/{slug}/lessons", response_model=dict)
def get_lessons(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject_repo = SubjectRepository(db)
    subject = subject_repo.get_by_slug(slug)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    lesson_repo = LessonRepository(db)
    lessons = lesson_repo.get_by_subject(subject.id)

    return {
        "lessons": [
            {
                "id": str(l.id),
                "title": l.title,
                "slug": l.slug,
                "summary": l.summary,
                "order_index": l.order_index,
                "estimated_minutes": l.estimated_minutes,
            }
            for l in lessons
        ]
    }


@router.get("/{slug}/lessons/{lesson_slug}", response_model=dict)
def get_lesson_detail(
    slug: str,
    lesson_slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject_repo = SubjectRepository(db)
    subject = subject_repo.get_by_slug(slug)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    lesson_repo = LessonRepository(db)
    lesson = lesson_repo.get_by_slug(lesson_slug)
    if not lesson or lesson.subject_id != subject.id:
        raise HTTPException(status_code=404, detail="Lesson not found")

    topics = lesson_repo.get_topics(lesson.id)

    return {
        "id": str(lesson.id),
        "title": lesson.title,
        "slug": lesson.slug,
        "content": lesson.content,
        "summary": lesson.summary,
        "estimated_minutes": lesson.estimated_minutes,
        "order_index": lesson.order_index,
        "topics": [
            {
                "id": str(t.id),
                "title": t.title,
                "content": t.content,
                "order_index": t.order_index,
            }
            for t in topics
        ],
    }