import io
import uuid
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.services.file_storage_service import FileUploadService


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
        "email": f"fu_{tag}@example.com",
        "password": "TestPassword123!",
        "full_name": "File Upload Test User",
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


def _seed_ocr_file(client, token, user_id, ocr_status="pending", ocr_text=None):
    from app.models.uploaded_file import UploadedFile
    db, gen = _get_db()
    try:
        f = UploadedFile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            original_filename="ocr_test.pdf",
            stored_filename="stored_test.pdf",
            mime_type="application/pdf",
            file_size=1024,
            storage_path="/tmp/test.pdf",
            ocr_status=ocr_status,
            ocr_text=ocr_text,
        )
        db.add(f)
        db.commit()
        return f.id
    finally:
        _close_db(db, gen)


class TestUploadFile:

    def test_valid_pdf_upload(self, client: TestClient):
        token, user = _signup(client, "upload_valid")
        content = b"fake pdf content"
        resp = client.post("/api/files/upload", files={
            "file": ("test.pdf", io.BytesIO(content), "application/pdf"),
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_filename"] == "test.pdf"
        assert data["mime_type"] == "application/pdf"
        assert data["file_size"] == len(content)
        assert data["ocr_status"] == "pending"
        assert "id" in data

    def test_valid_png_upload(self, client: TestClient):
        token, user = _signup(client, "upload_png")
        content = b"fake png content"
        resp = client.post("/api/files/upload", files={
            "file": ("image.png", io.BytesIO(content), "image/png"),
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["mime_type"] == "image/png"

    def test_missing_filename_rejected(self, client: TestClient):
        token, user = _signup(client, "upload_nofn")
        resp = client.post("/api/files/upload", files={
            "file": (None, io.BytesIO(b"content"), "application/pdf"),
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code in (400, 422)

    def test_file_too_large(self, client: TestClient):
        token, user = _signup(client, "upload_toolarge")
        with patch.object(FileUploadService, "validate_file", side_effect=ValueError("File too large. Maximum size is 50MB")):
            resp = client.post("/api/files/upload", files={
                "file": ("big.pdf", io.BytesIO(b"x" * 1000), "application/pdf"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 400
        assert "File too large" in resp.json()["detail"]

    def test_file_size_boundary_pass(self, client: TestClient):
        token, user = _signup(client, "upload_bndpass")
        # MAX_UPLOAD_SIZE_MB=0.0001 => max_size ≈ 104 bytes; 100 bytes is within limit
        with patch("app.services.file_storage_service.settings.MAX_UPLOAD_SIZE_MB", 0.0001):
            content = b"x" * 100
            resp = client.post("/api/files/upload", files={
                "file": ("exact.pdf", io.BytesIO(content), "application/pdf"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_file_size_boundary_fail(self, client: TestClient):
        token, user = _signup(client, "upload_bndfail")
        # MAX_UPLOAD_SIZE_MB=0.0001 => max_size ≈ 104 bytes; 105 bytes exceeds limit
        with patch("app.services.file_storage_service.settings.MAX_UPLOAD_SIZE_MB", 0.0001):
            resp = client.post("/api/files/upload", files={
                "file": ("over.pdf", io.BytesIO(b"x" * 105), "application/pdf"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 400
        assert "File too large" in resp.json()["detail"]

    def test_invalid_mime_type(self, client: TestClient):
        token, user = _signup(client, "upload_badmime")
        with patch.object(FileUploadService, "validate_file", side_effect=ValueError("File type 'text/plain' is not allowed")):
            resp = client.post("/api/files/upload", files={
                "file": ("test.txt", io.BytesIO(b"text"), "text/plain"),
            }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 400
        assert "not allowed" in resp.json()["detail"]

    def test_filename_with_special_chars(self, client: TestClient):
        token, user = _signup(client, "upload_special")
        content = b"data"
        resp = client.post("/api/files/upload", files={
            "file": ("my file (1).pdf", io.BytesIO(content), "application/pdf"),
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["original_filename"] == "my file (1).pdf"

    def test_very_long_filename(self, client: TestClient):
        token, user = _signup(client, "upload_longfn")
        long_name = "a" * 490 + ".pdf"
        content = b"data"
        resp = client.post("/api/files/upload", files={
            "file": (long_name, io.BytesIO(content), "application/pdf"),
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["original_filename"] == long_name

    def test_sql_injection_filename(self, client: TestClient):
        token, user = _signup(client, "upload_sqli")
        content = b"data"
        resp = client.post("/api/files/upload", files={
            "file": ("'; DROP TABLE users; --.pdf", io.BytesIO(content), "application/pdf"),
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["original_filename"] == "'; DROP TABLE users; --.pdf"
        db, gen = _get_db()
        try:
            from app.models.user import User
            count = db.query(User).count()
            assert count >= 1
        finally:
            _close_db(db, gen)

    def test_unauthorized(self, client: TestClient):
        resp = client.post("/api/files/upload", files={
            "file": ("test.pdf", io.BytesIO(b"x"), "application/pdf"),
        })
        assert resp.status_code in (401, 403)


class TestListFiles:

    def test_empty_list(self, client: TestClient):
        token, user = _signup(client, "list_empty")
        resp = client.get("/api/files", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["files"] == []
        assert data["total"] == 0

    def test_with_files(self, client: TestClient):
        token, user = _signup(client, "list_with")
        client.post("/api/files/upload", files={
            "file": ("a.pdf", io.BytesIO(b"aaa"), "application/pdf"),
        }, headers={"Authorization": f"Bearer {token}"})
        client.post("/api/files/upload", files={
            "file": ("b.pdf", io.BytesIO(b"bbb"), "application/pdf"),
        }, headers={"Authorization": f"Bearer {token}"})
        resp = client.get("/api/files", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["files"]) == 2

    def test_pagination(self, client: TestClient):
        token, user = _signup(client, "list_page")
        for i in range(5):
            client.post("/api/files/upload", files={
                "file": (f"file{i}.pdf", io.BytesIO(b"x"), "application/pdf"),
            }, headers={"Authorization": f"Bearer {token}"})
        resp = client.get("/api/files?skip=2&limit=2", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 5
        assert len(data["files"]) == 2

    def test_other_user_files_not_visible(self, client: TestClient):
        token1, user1 = _signup(client, "list_other1")
        token2, user2 = _signup(client, "list_other2")
        client.post("/api/files/upload", files={
            "file": ("secret.pdf", io.BytesIO(b"secret"), "application/pdf"),
        }, headers={"Authorization": f"Bearer {token1}"})
        resp = client.get("/api/files", headers={"Authorization": f"Bearer {token2}"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 0


class TestGetOcrStatus:

    def test_pending(self, client: TestClient):
        token, user = _signup(client, "ocr_pending")
        file_id = _seed_ocr_file(client, token, user["id"], ocr_status="pending")
        resp = client.get(f"/api/files/{file_id}/ocr-status", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["ocr_status"] == "pending"

    def test_completed(self, client: TestClient):
        token, user = _signup(client, "ocr_done")
        file_id = _seed_ocr_file(client, token, user["id"], ocr_status="completed", ocr_text="Extracted text content")
        resp = client.get(f"/api/files/{file_id}/ocr-status", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["ocr_status"] == "completed"
        assert data["ocr_text"] == "Extracted text content"

    def test_failed(self, client: TestClient):
        token, user = _signup(client, "ocr_fail")
        file_id = _seed_ocr_file(client, token, user["id"], ocr_status="failed")
        resp = client.get(f"/api/files/{file_id}/ocr-status", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["ocr_status"] == "failed"

    def test_not_found(self, client: TestClient):
        token, user = _signup(client, "ocr_nf")
        resp = client.get("/api/files/nonexistent-id/ocr-status", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_wrong_user_cannot_access(self, client: TestClient):
        token1, user1 = _signup(client, "ocr_wrong1")
        token2, user2 = _signup(client, "ocr_wrong2")
        file_id = _seed_ocr_file(client, token1, user1["id"])
        resp = client.get(f"/api/files/{file_id}/ocr-status", headers={"Authorization": f"Bearer {token2}"})
        assert resp.status_code == 404


class TestUploadEdgeCases:

    def test_jpeg_upload(self, client: TestClient):
        token, user = _signup(client, "edge_jpeg")
        resp = client.post("/api/files/upload", files={
            "file": ("photo.jpg", io.BytesIO(b"jpeg data"), "image/jpeg"),
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["mime_type"] == "image/jpeg"

    def test_webp_upload(self, client: TestClient):
        token, user = _signup(client, "edge_webp")
        resp = client.post("/api/files/upload", files={
            "file": ("img.webp", io.BytesIO(b"webp data"), "image/webp"),
        }, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_missing_file_field(self, client: TestClient):
        token, user = _signup(client, "edge_nofile")
        resp = client.post("/api/files/upload", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422

    def test_upload_then_list_has_ocr_pending(self, client: TestClient):
        token, user = _signup(client, "edge_upload_list")
        client.post("/api/files/upload", files={
            "file": ("new.pdf", io.BytesIO(b"data"), "application/pdf"),
        }, headers={"Authorization": f"Bearer {token}"})
        resp = client.get("/api/files", headers={"Authorization": f"Bearer {token}"})
        assert resp.json()["files"][0]["ocr_status"] == "pending"
