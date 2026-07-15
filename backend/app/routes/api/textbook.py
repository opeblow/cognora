from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.base import get_db
from app.dependencies.auth import get_current_user
from app.repositories.subject import SubjectRepository
from app.models.user import User
from app.models.subject import Subject
from app.models.lesson import Topic
from app.schemas.textbook import (
    TextbookPlanResponse,
    TextbookStatusResponse,
    SectionPlan,
    SectionContent,
    GenerateSectionResponse,
    GenerateSectionRequest,
)
from app.services.textbook_service import TextbookService, generate_section_content
from app.services.credit_service import CreditService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subjects/{slug}/topics/{topic_id}/textbook", tags=["Textbook"])


def _get_subject_and_topic(slug: str, topic_id: str, db: Session):
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

    return subject, topic


@router.get("/plan", response_model=TextbookPlanResponse)
def get_textbook_plan(
    slug: str,
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject, topic = _get_subject_and_topic(slug, topic_id, db)
    service = TextbookService()
    sections = service.get_section_plan()

    return TextbookPlanResponse(
        topic_id=topic_id,
        topic_title=topic.title,
        subject_name=subject.name,
        total_sections=len(sections),
        sections=[SectionPlan(**s) for s in sections],
    )


@router.get("/status", response_model=TextbookStatusResponse)
async def get_textbook_status(
    slug: str,
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject, topic = _get_subject_and_topic(slug, topic_id, db)
    service = TextbookService()
    sections = service.get_section_plan()
    generated = await service.get_generated_sections(topic_id)

    section_list = []
    for s in sections:
        section_list.append(SectionContent(
            index=s["index"],
            title=s["title"],
            content="",
            has_content=s["index"] in generated,
        ))

    return TextbookStatusResponse(
        topic_id=topic_id,
        total_sections=len(sections),
        generated_sections=generated,
        sections=section_list,
    )


@router.get("/sections/{section_index}", response_model=SectionContent)
async def get_section_content(
    slug: str,
    topic_id: str,
    section_index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject, topic = _get_subject_and_topic(slug, topic_id, db)
    service = TextbookService()
    sections = service.get_section_plan()

    if section_index < 0 or section_index >= len(sections):
        raise HTTPException(status_code=404, detail="Section not found")

    content = await service.get_cached_section(topic_id, section_index)

    return SectionContent(
        index=section_index,
        title=sections[section_index]["title"],
        content=content or "",
        has_content=content is not None,
    )


@router.post("/sections/{section_index}/generate", response_model=GenerateSectionResponse)
async def generate_section(
    slug: str,
    topic_id: str,
    section_index: int,
    request: GenerateSectionRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    subject, topic = _get_subject_and_topic(slug, topic_id, db)
    service = TextbookService()
    sections = service.get_section_plan()

    if section_index < 0 or section_index >= len(sections):
        raise HTTPException(status_code=404, detail="Section not found")

    if not request:
        request = GenerateSectionRequest()

    if not request.regenerate:
        cached = await service.get_cached_section(topic_id, section_index)
        if cached:
            return GenerateSectionResponse(
                section_index=section_index,
                total_sections=len(sections),
                content=cached,
                section_title=sections[section_index]["title"],
                has_more=section_index < len(sections) - 1,
            )

    credit_service = CreditService(db)
    try:
        credit_service.deduct_credits(str(current_user.id), "ai_ask")
    except ValueError as e:
        raise HTTPException(status_code=402, detail=str(e))

    previous_sections = []
    for i in range(section_index):
        prev = await service.get_cached_section(topic_id, i)
        previous_sections.append(prev or "")

    try:
        content = await generate_section_content(
            subject=subject.name,
            topic=topic.title,
            section_index=section_index,
            previous_sections=previous_sections,
        )

        await service.cache_section(topic_id, section_index, content)

        return GenerateSectionResponse(
            section_index=section_index,
            total_sections=len(sections),
            content=content,
            section_title=sections[section_index]["title"],
            has_more=section_index < len(sections) - 1,
        )
    except ValueError as e:
        try:
            credit_service.add_credits(str(current_user.id), 1, description="Textbook generation failed — refund")
        except Exception:
            pass
        raise HTTPException(status_code=502, detail=str(e))
