import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.workers.celery_app import celery_app
from app.database.base import SessionLocal, engine, Base
from app.repositories.user import UserRepository
from app.models.user import User
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(queue="cpu")
def reset_weekly_credits():
    from sqlalchemy import update
    from app.models.user import User

    db = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        stmt = (
            update(User)
            .where(User.weekly_credits_reset_at <= now)
            .values(
                weekly_credits_used=0,
                weekly_credits_reset_at=now + timedelta(days=7)
            )
        )
        db.execute(stmt)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to reset weekly credits: {e}")
        db.rollback()
    finally:
        db.close()


@celery_app.task(queue="io")
def send_email(to: str, subject: str, body: str):
    from app.utils.email import EmailService
    service = EmailService()
    service.send_email(to, subject, body)


@celery_app.task(queue="cpu")
def cleanup_expired_tokens():
    db = SessionLocal()
    try:
        from app.models.user import EmailVerification, PasswordReset
        from sqlalchemy import delete

        now = datetime.now(timezone.utc)
        db.execute(
            delete(EmailVerification).where(EmailVerification.expires_at < now)
        )
        db.execute(
            delete(PasswordReset).where(PasswordReset.expires_at < now)
        )
        db.commit()
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, queue="io")
def process_ocr(self, file_id: str):
    from app.services.ocr_service import OcrService
    from app.services.file_storage_service import FileUploadService

    db = SessionLocal()
    try:
        service = FileUploadService(db)
        record = service.get_file_by_id(file_id)
        if not record:
            logger.error(f"OCR task: file {file_id} not found")
            return

        service.update_ocr_status(file_id, "processing")

        ocr = OcrService()
        text = ocr.extract_text(record.storage_path, record.mime_type)

        service.update_ocr_status(file_id, "completed", ocr_text=text)
        logger.info(f"OCR completed for file {file_id} ({len(text)} chars)")
    except Exception as exc:
        logger.error(f"OCR failed for file {file_id}: {exc}")
        try:
            fs = FileUploadService(db)
            fs.update_ocr_status(file_id, "failed")
        except Exception:
            pass
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, queue="io")
def transcribe_audio(self, audio_id: str):
    from app.services.audio_service import AudioService
    from app.models.audio_recording import AudioRecording

    db = SessionLocal()
    try:
        record = db.query(AudioRecording).filter(
            AudioRecording.id == audio_id
        ).first()
        if not record:
            logger.error(f"Transcribe task: audio {audio_id} not found")
            return

        record.processing_status = "processing"
        db.commit()

        service = AudioService()
        transcript = service.transcribe(record.file_path)
        record.transcript = transcript
        record.processing_status = "completed"
        db.commit()

        logger.info(f"Transcription completed for audio {audio_id} ({len(transcript)} chars)")
    except Exception as exc:
        logger.error(f"Transcription failed for audio {audio_id}: {exc}")
        try:
            if 'record' in locals():
                record.processing_status = "failed"
                db.commit()
        except Exception:
            pass
        raise self.retry(exc=exc)
    finally:
        db.close()


def _run_async(coro):
    import asyncio
    try:
        return asyncio.run(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30, queue="io")
def pre_generate_textbook_sections(self):
    from sqlalchemy import select
    from app.models.lesson import Topic, Lesson
    from app.services.textbook_service import TextbookService, generate_section_content

    db = SessionLocal()
    try:
        topics = db.execute(
            select(Topic).join(Topic.lesson).join(Lesson.subject)
        ).scalars().all()

        if not topics:
            logger.info("No topics found for pre-generation")
            return

        service = TextbookService()
        sections = service.get_section_plan()
        generated_count = 0

        for topic in topics:
            lesson = topic.lesson
            subject = lesson.subject
            if not subject:
                continue

            for section in sections:
                cached = _run_async(service.get_cached_section(str(topic.id), section["index"]))
                if cached:
                    continue

                previous_sections = []
                for i in range(section["index"]):
                    prev = _run_async(service.get_cached_section(str(topic.id), i))
                    previous_sections.append(prev or "")

                try:
                    content = _run_async(generate_section_content(
                        subject=subject.name,
                        topic=topic.title,
                        section_index=section["index"],
                        previous_sections=previous_sections,
                    ))
                    _run_async(service.cache_section(str(topic.id), section["index"], content))
                    generated_count += 1
                    logger.info(
                        f"Pre-generated: {subject.name} / {topic.title} / section {section['index']} ({generated_count} total)"
                    )
                except Exception as e:
                    logger.error(
                        f"Failed pre-generating {subject.name} / {topic.title} / section {section['index']}: {e}"
                    )
                    # Skip to the next section or topic instead of raising and retrying the whole task
                    continue

        logger.info(f"Pre-generation complete. Generated {generated_count} new sections.")
    except Exception as exc:
        logger.error(f"Pre-generation task failed: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60, queue="io")
def review_content_issue(self, issue_id: str):
    import json
    from openai import OpenAI

    db = SessionLocal()
    try:
        from app.models.content_issue import ContentIssue
        from app.models.lesson import Topic
        from app.models.textbook_section import TextbookSection

        issue = db.query(ContentIssue).filter(ContentIssue.id == issue_id).first()
        if not issue:
            logger.error(f"Issue {issue_id} not found")
            return

        content = None
        if issue.content_type == "topic":
            topic = db.query(Topic).filter(Topic.id == issue.content_id).first()
            content = topic.content if topic else None
        elif issue.content_type == "section" and issue.section_index is not None:
            section = (
                db.query(TextbookSection)
                .filter(
                    TextbookSection.topic_id == issue.content_id,
                    TextbookSection.section_index == issue.section_index,
                )
                .first()
            )
            content = section.content if section else None

        if not content:
            content = "[Content not found in database]"

        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = f"""A user reported an issue with AI-generated educational content.

Severity: {issue.severity}
Description: {issue.description}

Original content:
{content[:4000]}

Respond in JSON format:
{{"is_valid": true/false, "acknowledgment": "string explaining the finding", "suggested_fix": "corrected version or null if not needed"}}"""

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
        )
        result = json.loads(response.choices[0].message.content)

        issue.ai_response = result.get("acknowledgment", "")
        issue.status = "acknowledged"
        if result.get("suggested_fix"):
            issue.resolved_at = datetime.now(timezone.utc)

        db.commit()
        logger.info(f"Reviewed issue {issue_id}: {result.get('is_valid')}")
    except Exception as exc:
        logger.error(f"Failed to review issue {issue_id}: {exc}")
        raise self.retry(exc=exc)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30, autoretry_for=(Exception,), queue="io")
def pre_generate_question_pool(self):
    from sqlalchemy import select, func
    from app.models.subject import Subject
    from app.models.question_pool import QuestionPool
    from app.models.lesson import Topic
    from app.services.question_pool_service import QuestionPoolService

    db = SessionLocal()
    try:
        subjects = db.execute(select(Subject)).scalars().all()
        if not subjects:
            logger.info("No subjects found for question pool pre-generation")
            return

        pool_service = QuestionPoolService(db)
        generated_total = 0

        for subject in subjects:
            count_query = select(func.count()).select_from(QuestionPool).where(
                QuestionPool.subject_id == subject.id,
                QuestionPool.is_active == True
            )
            current_count = db.execute(count_query).scalar() or 0

            target_count = 50
            if current_count < target_count:
                needed = min(20, target_count - current_count)
                logger.info(f"Subject {subject.name} has {current_count} questions. Pre-generating {needed} more...")
                
                topic_objs = (
                    db.query(Topic)
                    .join(Topic.lesson)
                    .filter(Topic.lesson.has(subject_id=subject.id))
                    .all()
                )
                topics = [t.title for t in topic_objs]
                if not topics:
                    topics = ["general"]

                try:
                    new_qs = pool_service._generate_questions(str(subject.id), topics, needed)
                    generated_total += len(new_qs)
                    logger.info(f"Generated {len(new_qs)} new questions for {subject.name}")
                except Exception as e:
                    logger.error(f"Failed pre-generating questions for {subject.name}: {e}")

        logger.info(f"Question pool pre-generation complete. Generated {generated_total} new questions.")
    except Exception as exc:
        logger.error(f"Question pool pre-generation task failed: {exc}")
        raise
    finally:
        db.close()
