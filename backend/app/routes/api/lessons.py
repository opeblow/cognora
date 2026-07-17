from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.repositories.subject import SubjectRepository
from app.repositories.lesson import LessonRepository
from app.models.user import User
from app.models.subject import Subject
from app.models.lesson import Topic, Lesson
from app.services.ai_service import AIService
from app.services.credit_service import CreditService

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
                "content_type": "ai_expanded" if t.content and len(t.content) > 2000 else "basic",
                "order_index": t.order_index,
            }
            for t in topics
        ],
    }


@router.get("/{slug}/topics", response_model=dict)
def get_topics_by_subject(
    slug: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subject_repo = SubjectRepository(db)
    subject = subject_repo.get_by_slug(slug)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    topics = db.execute(
        select(Topic)
        .join(Lesson, Topic.lesson_id == Lesson.id)
        .where(Lesson.subject_id == subject.id)
        .order_by(Lesson.order_index, Topic.order_index)
    ).scalars().all()

    return {
        "topics": [
            {
                "id": str(t.id),
                "title": t.title,
                "content": t.content,
                "content_type": "ai_expanded" if t.content and len(t.content) > 2000 else "basic",
                "order_index": t.order_index,
                "lesson_title": t.lesson.title if t.lesson else None,
            }
            for t in topics
        ]
    }


@router.get("/{slug}/topics/{topic_id}", response_model=dict)
def get_topic_detail(
    slug: str,
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject_repo = SubjectRepository(db)
    subject = subject_repo.get_by_slug(slug)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    topic = db.execute(select(Topic).where(Topic.id == topic_id)).scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    lesson = topic.lesson
    if lesson.subject_id != subject.id:
        raise HTTPException(status_code=404, detail="Topic not found in this subject")

    has_expanded = topic.content and len(topic.content) > 2000

    all_topics = db.execute(
        select(Topic)
        .join(Lesson, Topic.lesson_id == Lesson.id)
        .where(Lesson.subject_id == subject.id)
        .order_by(Lesson.order_index, Topic.order_index)
    ).scalars().all()

    return {
        "id": str(topic.id),
        "title": topic.title,
        "content": topic.content,
        "has_expanded": has_expanded,
        "lesson": {
            "id": str(lesson.id),
            "title": lesson.title,
            "slug": lesson.slug,
        },
        "subject": {
            "id": str(subject.id),
            "name": subject.name,
            "slug": subject.slug,
            "color": subject.color,
        },
        "all_topics": [
            {
                "id": str(t.id),
                "title": t.title,
                "order_index": t.order_index,
            }
            for t in all_topics
        ],
    }


@router.post("/{slug}/topics/{topic_id}/expand", response_model=dict)
def expand_topic_content(
    slug: str,
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject_repo = SubjectRepository(db)
    subject = subject_repo.get_by_slug(slug)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    topic = db.execute(select(Topic).where(Topic.id == topic_id)).scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    credit_service = CreditService(db)
    try:
        credit_service.deduct_credits(str(current_user.id), "ai_ask")
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    ai_service = AIService()
    try:
        generated = ai_service.generate_textbook_content(
            subject=subject.name,
            topic=topic.title,
            existing_content=topic.content or "",
        )

        topic.content = generated
        db.commit()

        return {"content": generated, "expanded": True, "subject": subject.name, "topic": topic.title}
    except ValueError as e:
        try:
            credit_service.add_credits(str(current_user.id), 1, description="Content expansion failed — refund")
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=str(e))