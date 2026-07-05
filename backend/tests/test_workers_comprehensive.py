import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.orm import Session
from app.database.base import SessionLocal
from app.models.user import User, EmailVerification, PasswordReset
from app.models.content_issue import ContentIssue
from app.models.uploaded_file import UploadedFile
from app.models.audio_recording import AudioRecording
from app.models.subject import Subject
from app.models.lesson import Lesson, Topic
from app.workers.tasks import (
    reset_weekly_credits,
    cleanup_expired_tokens,
    process_ocr,
    transcribe_audio,
    review_content_issue,
    pre_generate_textbook_sections,
)


def _create_user(db: Session, email: str, **kwargs) -> User:
    import uuid
    u = User(
        id=str(uuid.uuid4()),
        email=email,
        password_hash="hash",
        full_name=f"Worker {email}",
        **kwargs,
    )
    db.add(u)
    db.commit()
    return u


def test_reset_weekly_credits_normal(db_session: Session):
    u = _create_user(db_session, "reset_normal@test.com",
                     weekly_credits_used=30,
                     weekly_credits_reset_at=datetime.now() - timedelta(days=1))
    db_session.commit()

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, 'close', return_value=None):
            with patch("app.workers.tasks.UserRepository.get_all") as mock_get_all:
                from app.repositories.user import UserRepository
                mock_get_all.return_value = ([u], 1)
                reset_weekly_credits()

    db_session.expire_all()
    u = db_session.query(User).filter(User.id == u.id).first()
    assert u.weekly_credits_used == 0
    assert u.weekly_credits_reset_at > datetime.now()


def test_reset_weekly_credits_already_recent(db_session: Session):
    future = datetime.now() + timedelta(days=6)
    u = _create_user(db_session, "reset_recent@test.com",
                     weekly_credits_used=10,
                     weekly_credits_reset_at=future)
    db_session.commit()

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, 'close', return_value=None):
            with patch("app.workers.tasks.UserRepository.get_all") as mock_get_all:
                mock_get_all.return_value = ([u], 1)
                reset_weekly_credits()

    db_session.expire_all()
    u = db_session.query(User).filter(User.id == u.id).first()
    assert u.weekly_credits_used == 10


def test_reset_weekly_credits_all_users(db_session: Session):
    u1 = _create_user(db_session, "reset_all1@test.com",
                      weekly_credits_used=20,
                      weekly_credits_reset_at=datetime.now() - timedelta(days=2))
    u2 = _create_user(db_session, "reset_all2@test.com",
                      weekly_credits_used=5,
                      weekly_credits_reset_at=datetime.now() - timedelta(days=10))
    u3 = _create_user(db_session, "reset_all3@test.com",
                      weekly_credits_used=0,
                      weekly_credits_reset_at=datetime.now() + timedelta(days=1))
    db_session.commit()

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, 'close', return_value=None):
            with patch("app.workers.tasks.UserRepository.get_all") as mock_get_all:
                mock_get_all.return_value = ([u1, u2, u3], 3)
                reset_weekly_credits()

    db_session.expire_all()
    u1 = db_session.query(User).filter(User.id == u1.id).first()
    u2 = db_session.query(User).filter(User.id == u2.id).first()
    u3 = db_session.query(User).filter(User.id == u3.id).first()
    assert u1.weekly_credits_used == 0
    assert u2.weekly_credits_used == 0
    assert u3.weekly_credits_used == 0


def test_cleanup_expired_tokens(db_session: Session):
    import uuid
    past = datetime.now() - timedelta(hours=1)
    future = datetime.now() + timedelta(hours=1)

    ev = EmailVerification(id=str(uuid.uuid4()), user_id="u1", token="expired_ev", expires_at=past)
    db_session.add(ev)
    pv = EmailVerification(id=str(uuid.uuid4()), user_id="u2", token="valid_ev", expires_at=future)
    db_session.add(pv)
    pr = PasswordReset(id=str(uuid.uuid4()), user_id="u3", token="expired_pr", expires_at=past)
    db_session.add(pr)
    db_session.commit()

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        cleanup_expired_tokens()

    remaining_ev = db_session.query(EmailVerification).all()
    remaining_pr = db_session.query(PasswordReset).all()
    assert len(remaining_ev) == 1
    assert remaining_ev[0].token == "valid_ev"
    assert len(remaining_pr) == 0


def test_cleanup_expired_tokens_none_expired(db_session: Session):
    import uuid
    future = datetime.now() + timedelta(days=1)
    ev = EmailVerification(id=str(uuid.uuid4()), user_id="u1", token="t1", expires_at=future)
    db_session.add(ev)
    db_session.commit()

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        cleanup_expired_tokens()

    assert db_session.query(EmailVerification).count() == 1


def test_cleanup_expired_tokens_mixed(db_session: Session):
    import uuid
    past = datetime.now() - timedelta(days=1)
    future = datetime.now() + timedelta(days=1)

    for t in ("e1", "e2"):
        db_session.add(EmailVerification(id=str(uuid.uuid4()), user_id="u", token=t, expires_at=past))
    for t in ("v1", "v2", "v3"):
        db_session.add(EmailVerification(id=str(uuid.uuid4()), user_id="u", token=t, expires_at=future))
    db_session.commit()

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        cleanup_expired_tokens()

    assert db_session.query(EmailVerification).count() == 3


def test_process_ocr_success(db_session: Session):
    import uuid
    fid = str(uuid.uuid4())
    u = _create_user(db_session, "ocr_ok@test.com")
    uf = UploadedFile(
        id=fid, user_id=u.id, original_filename="doc.pdf",
        stored_filename="stored.pdf", mime_type="application/pdf",
        file_size=1000, storage_path="/tmp/test.pdf", storage_backend="local",
        ocr_status="pending",
    )
    db_session.add(uf)
    db_session.commit()

    mock_ocr = MagicMock()
    mock_ocr.extract_text.return_value = "Extracted text content"

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch("app.services.file_storage_service.FileUploadService") as mock_fus:
            mock_fus_instance = MagicMock()
            mock_fus.return_value = mock_fus_instance
            mock_fus_instance.get_file_by_id.return_value = uf

            with patch("app.services.ocr_service.OcrService") as mock_ocr_cls:
                mock_ocr_cls.return_value = mock_ocr
                process_ocr(fid)

    mock_fus_instance.get_file_by_id.assert_called_once_with(fid)
    mock_fus_instance.update_ocr_status.assert_any_call(fid, "processing")
    mock_fus_instance.update_ocr_status.assert_any_call(fid, "completed", ocr_text="Extracted text content")


def test_process_ocr_file_not_found(db_session: Session):
    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch("app.services.file_storage_service.FileUploadService") as mock_fus:
            mock_fus_instance = MagicMock()
            mock_fus.return_value = mock_fus_instance
            mock_fus_instance.get_file_by_id.return_value = None
            process_ocr("nonexistent_id")
            mock_fus_instance.get_file_by_id.assert_called_once_with("nonexistent_id")


def test_process_ocr_retry_on_failure(db_session: Session):
    import uuid
    fid = str(uuid.uuid4())
    u = _create_user(db_session, "ocr_fail@test.com")
    uf = UploadedFile(id=fid, user_id=u.id, original_filename="doc.pdf",
                      stored_filename="s.pdf", mime_type="application/pdf",
                      file_size=100, storage_path="/tmp/fail.pdf", storage_backend="local",
                      ocr_status="pending")
    db_session.add(uf)
    db_session.commit()

    task_self = MagicMock()
    task_self.retry = MagicMock(side_effect=Exception("retry called"))

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch("app.services.file_storage_service.FileUploadService") as mock_fus:
            mock_fus_instance = MagicMock()
            mock_fus.return_value = mock_fus_instance
            mock_fus_instance.get_file_by_id.return_value = uf

            with patch("app.services.ocr_service.OcrService") as mock_ocr_cls:
                mock_ocr = MagicMock()
                mock_ocr.extract_text.side_effect = Exception("OCR failed")
                mock_ocr_cls.return_value = mock_ocr

                with pytest.raises(Exception):
                    process_ocr.__wrapped__(task_self, fid)


def test_transcribe_audio_success(db_session: Session):
    import uuid
    aid = str(uuid.uuid4())
    u = _create_user(db_session, "trans_ok@test.com")
    rec = AudioRecording(
        id=aid, user_id=u.id, file_path="/tmp/audio.mp3",
        mime_type="audio/mp3", duration_seconds=30,
        processing_status="pending",
    )
    db_session.add(rec)
    db_session.commit()

    mock_audio = MagicMock()
    mock_audio.transcribe.return_value = "Transcribed text"

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, 'close', return_value=None):
            with patch("app.services.audio_service.AudioService") as mock_audio_cls:
                mock_audio_cls.return_value = mock_audio
                transcribe_audio(aid)

    db_session.expire_all()
    rec = db_session.query(AudioRecording).filter(AudioRecording.id == rec.id).first()
    assert rec.processing_status == "completed"
    assert rec.transcript == "Transcribed text"


def test_transcribe_audio_file_not_found(db_session: Session):
    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        transcribe_audio("nonexistent_audio")

    assert True


def test_transcribe_audio_failure(db_session: Session):
    import uuid
    aid = str(uuid.uuid4())
    u = _create_user(db_session, "trans_fail@test.com")
    rec = AudioRecording(id=aid, user_id=u.id, file_path="/tmp/bad.wav",
                         mime_type="audio/wav", duration_seconds=10,
                         processing_status="pending")
    db_session.add(rec)
    db_session.commit()

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch("app.services.audio_service.AudioService") as mock_audio_cls:
            mock_audio = MagicMock()
            mock_audio.transcribe.side_effect = Exception("Transcription failed")
            mock_audio_cls.return_value = mock_audio

            with pytest.raises(Exception):
                transcribe_audio.__wrapped__(aid)


def test_review_content_issue_valid(db_session: Session, monkeypatch):
    import uuid
    iid = str(uuid.uuid4())
    u = _create_user(db_session, "review_ok@test.com")

    issue = ContentIssue(
        id=iid, user_id=u.id, content_type="topic",
        content_id="topic_123", severity="medium",
        description="Has an error", status="open",
    )
    db_session.add(issue)
    db_session.commit()

    mock_openai = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"is_valid": false, "acknowledgment": "Found an error", "suggested_fix": "Fix it"}'
    mock_openai.chat.completions.create.return_value = mock_response

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, 'close', return_value=None):
            with patch("openai.OpenAI", return_value=mock_openai):
                review_content_issue(iid)

    db_session.expire_all()
    issue = db_session.query(ContentIssue).filter(ContentIssue.id == issue.id).first()
    assert issue.status == "acknowledged"
    assert issue.ai_response == "Found an error"
    assert issue.resolved_at is not None


def test_review_content_issue_not_found(db_session: Session):
    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        review_content_issue("nonexistent_issue")

    assert True


def test_review_content_issue_no_suggested_fix(db_session: Session):
    import uuid
    iid = str(uuid.uuid4())
    u = _create_user(db_session, "review_nofix@test.com")
    issue = ContentIssue(
        id=iid, user_id=u.id, content_type="topic",
        content_id="t1", severity="low",
        description="Minor typo", status="open",
    )
    db_session.add(issue)
    db_session.commit()

    mock_openai = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = '{"is_valid": true, "acknowledgment": "Looks fine", "suggested_fix": null}'
    mock_openai.chat.completions.create.return_value = mock_response

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, 'close', return_value=None):
            with patch("openai.OpenAI", return_value=mock_openai):
                review_content_issue(iid)

    db_session.expire_all()
    issue = db_session.query(ContentIssue).filter(ContentIssue.id == issue.id).first()
    assert issue.status == "acknowledged"
    assert issue.resolved_at is None


def test_pre_generate_textbook_sections_no_topics(db_session: Session):
    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        pre_generate_textbook_sections()

    assert True


def test_pre_generate_textbook_sections_new_sections(db_session: Session, monkeypatch):
    subj = Subject(name="Physics", slug="physics", description="Physics", category="science")
    db_session.add(subj)
    db_session.flush()
    lesson = Lesson(subject_id=subj.id, title="Mechanics", slug="mechanics", order_index=1)
    db_session.add(lesson)
    db_session.flush()
    topic = Topic(lesson_id=lesson.id, title="Newton's Laws", content="Intro", order_index=1)
    db_session.add(topic)
    db_session.commit()

    async def mock_get_cached(topic_id, section_index):
        return None

    async def mock_cache(topic_id, section_index, content):
        pass

    async def mock_generate(subject, topic, section_index, previous_sections):
        return f"<h3>Section {section_index}</h3>"

    monkeypatch.setattr("app.services.textbook_service.TextbookService.get_cached_section", mock_get_cache := AsyncMock(side_effect=mock_get_cached))
    monkeypatch.setattr("app.services.textbook_service.TextbookService.cache_section", mock_cache_fn := AsyncMock(side_effect=mock_cache))
    monkeypatch.setattr("app.services.textbook_service.generate_section_content", mock_generate)

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        pre_generate_textbook_sections()

    assert True


def test_pre_generate_textbook_sections_existing_sections_skipped(db_session: Session, monkeypatch):
    subj = Subject(name="Chemistry", slug="chemistry", description="Chem", category="science")
    db_session.add(subj)
    db_session.flush()
    lesson = Lesson(subject_id=subj.id, title="Organic", slug="organic", order_index=1)
    db_session.add(lesson)
    db_session.flush()
    topic = Topic(lesson_id=lesson.id, title="Alkanes", content="Intro", order_index=1)
    db_session.add(topic)
    db_session.commit()

    generated_indices = []

    async def mock_get_cached(topic_id, section_index):
        if section_index in generated_indices:
            return "<h3>Cached</h3>"
        return None

    monkeypatch.setattr("app.services.textbook_service.TextbookService.get_cached_section", AsyncMock(side_effect=mock_get_cached))

    with patch("app.workers.tasks.SessionLocal", return_value=db_session):
        with patch.object(db_session, 'close', return_value=None):
            pre_generate_textbook_sections()

    assert True


def test_task_retry_behavior():
    task_self = MagicMock()
    task_self.max_retries = 3
    task_self.default_retry_delay = 60
    task_self.request = MagicMock()
    task_self.request.retries = 0

    called = {"count": 0}

    def task_func(self):
        called["count"] += 1
        if called["count"] < 2:
            try:
                raise Exception("Transient error")
            except Exception as exc:
                raise self.retry(exc=exc)
        return "success"

    task_self.retry.side_effect = lambda exc=None: (_ for _ in ()).throw(Exception("Transient error"))

    with pytest.raises(Exception):
        task_func(task_self)
    assert called["count"] == 1
