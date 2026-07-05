import io
import uuid
import json
import pytest
from unittest.mock import patch, MagicMock, PropertyMock, AsyncMock
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.services.audio_service import AudioService
from app.models.audio_recording import AudioRecording


class _MockRedisPipeline:
    def zadd(self, *args, **kw): return self
    def zremrangebyscore(self, *args, **kw): return self
    def zcard(self, *args, **kw): return self
    def expire(self, *args, **kw): return self
    async def execute(self): return [1, 1, 1, 1]


class _MockRedisClient:
    def pipeline(self): return _MockRedisPipeline()
    async def incr(self, key): return 1
    async def expire(self, key, ttl): return True


@pytest.fixture(autouse=True)
def _mock_redis(monkeypatch):
    async def mock_get_redis(): return _MockRedisClient()
    monkeypatch.setattr("app.database.redis.get_redis", mock_get_redis)
    monkeypatch.setattr("app.middleware.rate_limit.get_redis", mock_get_redis)


def _signup(client, tag):
    resp = client.post("/api/auth/signup", json={
        "email": f"au_{tag}@example.com",
        "password": "TestPassword123!",
        "full_name": "Audio Test User",
    })
    assert resp.status_code == 201
    data = resp.json()
    return data["access_token"], data["user"]


def _get_db():
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    return db, gen


def _close_db(db, gen):
    db.close()
    try:
        next(gen)
    except StopIteration:
        pass


def _seed_audio(user_id, status="pending", transcript=None, feedback=None):
    from app.models.audio_recording import AudioRecording
    db, gen = _get_db()
    try:
        rec = AudioRecording(
            id=str(uuid.uuid4()),
            user_id=user_id,
            file_path="/tmp/test_audio.webm",
            mime_type="audio/webm",
            transcript=transcript,
            ai_feedback=feedback,
            processing_status=status,
        )
        db.add(rec)
        db.commit()
        return rec.id
    finally:
        _close_db(db, gen)


class TestUploadAudio:

    def test_valid_webm_upload(self, client: TestClient):
        token, user = _signup(client, "upload_valid")
        content = b"fake audio content"
        with patch("app.workers.tasks.transcribe_audio.delay") as mock_celery:
            resp = client.post("/api/audio/upload", files={
                "file": ("recording.webm", io.BytesIO(content), "audio/webm"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["processing_status"] == "pending"
        assert "Transcription in progress" in data["message"]
        assert "id" in data
        mock_celery.assert_called_once()

    def test_valid_mp3_upload(self, client: TestClient):
        token, user = _signup(client, "upload_mp3")
        with patch("app.workers.tasks.transcribe_audio.delay"):
            resp = client.post("/api/audio/upload", files={
                "file": ("audio.mp3", io.BytesIO(b"mp3 data"), "audio/mp3"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_valid_wav_upload(self, client: TestClient):
        token, user = _signup(client, "upload_wav")
        with patch("app.workers.tasks.transcribe_audio.delay"):
            resp = client.post("/api/audio/upload", files={
                "file": ("sound.wav", io.BytesIO(b"wav data"), "audio/wav"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["processing_status"] == "pending"

    def test_file_too_large(self, client: TestClient):
        token, user = _signup(client, "upload_toolarge")
        import app.core.config as cfg
        original = cfg.settings.MAX_UPLOAD_SIZE_MB
        cfg.settings.MAX_UPLOAD_SIZE_MB = 1
        try:
            content = b"x" * (1024 * 1024 + 1)
            resp = client.post("/api/audio/upload", files={
                "file": ("big.webm", io.BytesIO(content), "audio/webm"),
            }, headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code == 400
            assert "File too large" in resp.json()["detail"]
        finally:
            cfg.settings.MAX_UPLOAD_SIZE_MB = original

    def test_file_size_boundary_under_limit(self, client: TestClient):
        token, user = _signup(client, "upload_bndpass")
        import app.core.config as cfg
        original = cfg.settings.MAX_UPLOAD_SIZE_MB
        cfg.settings.MAX_UPLOAD_SIZE_MB = 1
        try:
            content = b"x" * (1024 * 1024)
            with patch("app.workers.tasks.transcribe_audio.delay"):
                resp = client.post("/api/audio/upload", files={
                    "file": ("exact.webm", io.BytesIO(content), "audio/webm"),
                }, headers={"Authorization": f"Bearer {token}"})
            assert resp.status_code == 200
        finally:
            cfg.settings.MAX_UPLOAD_SIZE_MB = original

    def test_missing_filename_rejected(self, client: TestClient):
        token, user = _signup(client, "upload_nofn")
        resp = client.post("/api/audio/upload", files={
            "file": (None, io.BytesIO(b"audio"), "audio/webm"),
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code in (400, 422)

    def test_file_with_no_extension(self, client: TestClient):
        token, user = _signup(client, "upload_noext")
        with patch("app.workers.tasks.transcribe_audio.delay"):
            resp = client.post("/api/audio/upload", files={
                "file": ("recording", io.BytesIO(b"audio"), "audio/webm"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_very_long_filename(self, client: TestClient):
        token, user = _signup(client, "upload_longfn")
        long_name = "a" * 490 + ".webm"
        with patch("app.workers.tasks.transcribe_audio.delay"):
            resp = client.post("/api/audio/upload", files={
                "file": (long_name, io.BytesIO(b"audio"), "audio/webm"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_audio_saved_with_correct_initial_status(self, client: TestClient):
        token, user = _signup(client, "upload_status")
        with patch("app.workers.tasks.transcribe_audio.delay"):
            resp = client.post("/api/audio/upload", files={
                "file": ("test.webm", io.BytesIO(b"data"), "audio/webm"),
            }, headers={"Authorization": f"Bearer {token}"})
        audio_id = resp.json()["id"]
        db, gen = _get_db()
        try:
            rec = db.query(AudioRecording).filter(AudioRecording.id == audio_id).first()
            assert rec is not None
            assert rec.processing_status == "pending"
            assert rec.user_id == user["id"]
        finally:
            _close_db(db, gen)

    def test_unauthorized(self, client: TestClient):
        resp = client.post("/api/audio/upload", files={
            "file": ("test.webm", io.BytesIO(b"audio"), "audio/webm"),
        })
        assert resp.status_code in (401, 403)

    def test_wrong_mime_type_still_accepted(self, client: TestClient):
        token, user = _signup(client, "upload_wrongmime")
        with patch("app.workers.tasks.transcribe_audio.delay"):
            resp = client.post("/api/audio/upload", files={
                "file": ("test.pdf", io.BytesIO(b"audio"), "application/pdf"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        db, gen = _get_db()
        try:
            rec = db.query(AudioRecording).filter(AudioRecording.id == resp.json()["id"]).first()
            assert rec.mime_type == "application/pdf"
        finally:
            _close_db(db, gen)


class TestGetAudioStatus:

    def test_pending(self, client: TestClient):
        token, user = _signup(client, "status_pending")
        audio_id = _seed_audio(user["id"], status="pending")
        resp = client.get(f"/api/audio/{audio_id}/status", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["processing_status"] == "pending"
        assert data["transcript"] is None
        assert data["ai_feedback"] is None

    def test_completed(self, client: TestClient):
        token, user = _signup(client, "status_complete")
        audio_id = _seed_audio(user["id"], status="completed", transcript="Hello world", feedback="Great job!")
        resp = client.get(f"/api/audio/{audio_id}/status", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["processing_status"] == "completed"
        assert data["transcript"] == "Hello world"
        assert data["ai_feedback"] == "Great job!"

    def test_failed(self, client: TestClient):
        token, user = _signup(client, "status_failed")
        audio_id = _seed_audio(user["id"], status="failed")
        resp = client.get(f"/api/audio/{audio_id}/status", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["processing_status"] == "failed"

    def test_not_found(self, client: TestClient):
        token, user = _signup(client, "status_nf")
        resp = client.get("/api/audio/nonexistent-id/status", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_wrong_user(self, client: TestClient):
        token1, user1 = _signup(client, "status_wrong1")
        token2, user2 = _signup(client, "status_wrong2")
        audio_id = _seed_audio(user1["id"])
        resp = client.get(f"/api/audio/{audio_id}/status", headers={"Authorization": f"Bearer {token2}"})
        assert resp.status_code == 404


class TestProcessAudio:

    def test_already_completed(self, client: TestClient):
        token, user = _signup(client, "proc_done")
        audio_id = _seed_audio(user["id"], status="completed", transcript="Done", feedback="OK")
        resp = client.post(f"/api/audio/process/{audio_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Already processed"
        assert data["transcript"] == "Done"
        assert data["ai_feedback"] == "OK"

    def test_not_found(self, client: TestClient):
        token, user = _signup(client, "proc_nf")
        resp = client.post("/api/audio/process/nonexistent-id", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_triggers_celery_task(self, client: TestClient):
        token, user = _signup(client, "proc_celery")
        audio_id = _seed_audio(user["id"], status="pending")
        with patch("app.workers.tasks.transcribe_audio.delay") as mock_task:
            resp = client.post(f"/api/audio/process/{audio_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["message"] == "Processing started"
        assert data["audio_id"] == audio_id
        mock_task.assert_called_once_with(audio_id)

    def test_process_pending_triggers_reprocess(self, client: TestClient):
        token, user = _signup(client, "proc_reprocess")
        audio_id = _seed_audio(user["id"], status="pending")
        with patch("app.workers.tasks.transcribe_audio.delay") as mock_task:
            client.post(f"/api/audio/process/{audio_id}", headers={"Authorization": f"Bearer {token}"})
        mock_task.assert_called_once_with(audio_id)

    def test_wrong_user_cannot_process(self, client: TestClient):
        token1, user1 = _signup(client, "proc_wrong1")
        token2, user2 = _signup(client, "proc_wrong2")
        audio_id = _seed_audio(user1["id"])
        resp = client.post(f"/api/audio/process/{audio_id}", headers={"Authorization": f"Bearer {token2}"})
        assert resp.status_code == 404


class TestEdgeCases:

    def test_upload_then_status_flow(self, client: TestClient):
        token, user = _signup(client, "flow_full")
        with patch("app.workers.tasks.transcribe_audio.delay"):
            upload_resp = client.post("/api/audio/upload", files={
                "file": ("flow.webm", io.BytesIO(b"audio data"), "audio/webm"),
            }, headers={"Authorization": f"Bearer {token}"})
        audio_id = upload_resp.json()["id"]
        status_resp = client.get(f"/api/audio/{audio_id}/status", headers={"Authorization": f"Bearer {token}"})
        assert status_resp.status_code == 200
        assert status_resp.json()["processing_status"] == "pending"

    def test_upload_defaults_webm_when_no_extension(self, client: TestClient):
        token, user = _signup(client, "edge_noext_default")
        with patch("app.workers.tasks.transcribe_audio.delay"):
            resp = client.post("/api/audio/upload", files={
                "file": ("noext", io.BytesIO(b"data"), "audio/webm"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_upload_unknown_mime_type(self, client: TestClient):
        token, user = _signup(client, "edge_unknownmime")
        with patch("app.workers.tasks.transcribe_audio.delay"):
            resp = client.post("/api/audio/upload", files={
                "file": ("test.bin", io.BytesIO(b"binary"), "application/octet-stream"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        db, gen = _get_db()
        try:
            rec = db.query(AudioRecording).filter(AudioRecording.id == resp.json()["id"]).first()
            assert rec.mime_type == "application/octet-stream"
        finally:
            _close_db(db, gen)


class TestMockTranscriptionService:

    def test_transcribe_called_on_upload(self, client: TestClient):
        token, user = _signup(client, "mock_transcribe")
        with patch("app.workers.tasks.transcribe_audio.delay") as mock_celery:
            client.post("/api/audio/upload", files={
                "file": ("test.webm", io.BytesIO(b"audio data"), "audio/webm"),
            }, headers={"Authorization": f"Bearer {token}"})
        mock_celery.assert_called_once()
        args = mock_celery.call_args[0][0]
        assert args is not None

    def test_audio_service_transcribe_can_be_mocked(self):
        with patch.object(AudioService, "transcribe", return_value="Mocked transcript") as mock_t:
            svc = AudioService()
            result = svc.transcribe("/fake/path")
            assert result == "Mocked transcript"
            mock_t.assert_called_once_with("/fake/path")

    def test_audio_service_generate_feedback_can_be_mocked(self):
        with patch.object(AudioService, "generate_feedback", return_value="Mocked feedback") as mock_f:
            svc = AudioService()
            result = svc.generate_feedback("Hello", "Math", "Algebra")
            assert result == "Mocked feedback"
            mock_f.assert_called_once_with("Hello", "Math", "Algebra")
