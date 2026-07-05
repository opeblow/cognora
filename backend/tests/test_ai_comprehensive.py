import asyncio
import json
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.services.ai_service import AIService
from app.services.credit_service import CreditService
from app.database.base import get_db
from app.main import app


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
        "email": f"ai_{tag}@example.com",
        "password": "TestPassword123!",
        "full_name": "AI Test User",
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


def _set_user_credits(user_id, amount):
    db, gen = _get_db()
    try:
        from app.models.user import User
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.credits = amount
            db.commit()
    finally:
        _close_db(db, gen)


MOCK_TUTOR_RESPONSE = "This is a comprehensive explanation of the topic."
MOCK_QUIZ_JSON = json.dumps({
    "title": "Quiz on Algebra",
    "questions": [
        {
            "text": "What is x in 2x = 4?",
            "options": ["A) 1", "B) 2", "C) 3", "D) 4"],
            "correct_answer": "B",
            "explanation": "2x = 4, so x = 2",
            "difficulty": "easy",
        }
    ],
})


class TestTutorChat:

    def test_valid_request(self, client: TestClient):
        token, _ = _signup(client, "tchat_valid")
        with patch.object(AIService, "_call_openai", return_value=MOCK_TUTOR_RESPONSE):
            resp = client.post("/api/ai/tutor", json={"message": "Explain algebra"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["response"] == MOCK_TUTOR_RESPONSE
        assert data["suggestions"] == []

    def test_with_subject(self, client: TestClient):
        token, _ = _signup(client, "tchat_subj")
        with patch.object(AIService, "_call_openai") as mock:
            mock.return_value = "Math response"
            resp = client.post("/api/ai/tutor", json={"message": "Explain", "subject": "Mathematics"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        call_args = mock.call_args[0][0]
        system_msg = call_args[0]["content"]
        assert "Mathematics" in system_msg

    def test_with_context(self, client: TestClient):
        token, _ = _signup(client, "tchat_ctx")
        context = [
            {"role": "user", "content": "What is algebra?"},
            {"role": "assistant", "content": "Algebra is math with variables."},
        ]
        with patch.object(AIService, "_call_openai") as mock:
            mock.return_value = "Context response"
            resp = client.post("/api/ai/tutor", json={"message": "Tell more", "context": context}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        call_args = mock.call_args[0][0]
        assert len(call_args) == 4
        assert call_args[1]["content"] == "What is algebra?"
        assert call_args[2]["content"] == "Algebra is math with variables."
        assert call_args[3]["content"] == "Tell more"

    def test_context_overflow_truncated(self, client: TestClient):
        token, _ = _signup(client, "tchat_overflow")
        context = [{"role": "user", "content": f"Message {i}"} for i in range(15)]
        with patch.object(AIService, "_call_openai") as mock:
            mock.return_value = "Overflow response"
            resp = client.post("/api/ai/tutor", json={"message": "Final", "context": context}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        call_args = mock.call_args[0][0]
        assert len(call_args) == 12
        assert call_args[-1]["content"] == "Final"
        assert call_args[-2]["content"] == "Message 14"

    def test_empty_message_rejected(self, client: TestClient):
        token, _ = _signup(client, "tchat_empty")
        resp = client.post("/api/ai/tutor", json={"message": ""}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422

    def test_message_at_5000_boundary(self, client: TestClient):
        token, _ = _signup(client, "tchat_5000")
        msg = "a" * 5000
        with patch.object(AIService, "_call_openai", return_value="OK"):
            resp = client.post("/api/ai/tutor", json={"message": msg}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_message_over_5000_rejected(self, client: TestClient):
        token, _ = _signup(client, "tchat_5001")
        msg = "a" * 5001
        resp = client.post("/api/ai/tutor", json={"message": msg}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422

    def test_insufficient_credits(self, client: TestClient):
        token, user = _signup(client, "tchat_nocred")
        _set_user_credits(user["id"], 0)
        resp = client.post("/api/ai/tutor", json={"message": "Hello"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 402
        assert "credit" in resp.json()["detail"].lower()

    def test_credit_deducted_successfully(self, client: TestClient):
        token, user = _signup(client, "tchat_deduct")
        db, gen = _get_db()
        try:
            from app.models.user import User
            u = db.query(User).filter(User.id == user["id"]).first()
            u.credits = 5
            db.commit()
        finally:
            _close_db(db, gen)
        with patch.object(AIService, "_call_openai", return_value="OK"):
            resp = client.post("/api/ai/tutor", json={"message": "Hi"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        db, gen = _get_db()
        try:
            from app.models.user import User
            u = db.query(User).filter(User.id == user["id"]).first()
            assert u.credits == 4
        finally:
            _close_db(db, gen)

    def test_unauthorized_access(self, client: TestClient):
        resp = client.post("/api/ai/tutor", json={"message": "Hello"})
        assert resp.status_code in (401, 403)


class TestGenerateQuiz:

    def test_valid_request(self, client: TestClient):
        token, _ = _signup(client, "quiz_valid")
        with patch.object(AIService, "_call_openai", return_value=MOCK_QUIZ_JSON):
            resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra", "difficulty": "medium", "num_questions": 1}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Quiz on Algebra"
        assert len(data["questions"]) == 1

    def test_valid_request_default_difficulty(self, client: TestClient):
        token, _ = _signup(client, "quiz_defdiff")
        with patch.object(AIService, "_call_openai", return_value='{"title":"Quiz","questions":[]}'):
            resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_ai_service_error(self, client: TestClient):
        token, _ = _signup(client, "quiz_aierr")
        with patch.object(AIService, "_call_openai", side_effect=ValueError("OpenAI API error")):
            resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 502

    def test_insufficient_credits(self, client: TestClient):
        token, user = _signup(client, "quiz_nocred")
        _set_user_credits(user["id"], 1)
        resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 402

    def test_credit_deducted_for_quiz(self, client: TestClient):
        token, user = _signup(client, "quiz_deduct")
        _set_user_credits(user["id"], 10)
        with patch.object(AIService, "_call_openai", return_value='{"title":"Quiz","questions":[]}'):
            resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        db, gen = _get_db()
        try:
            from app.models.user import User
            u = db.query(User).filter(User.id == user["id"]).first()
            assert u.credits == 8
        finally:
            _close_db(db, gen)

    def test_unauthorized(self, client: TestClient):
        resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra"})
        assert resp.status_code in (401, 403)


class TestCreditEdgeCases:

    def test_unknown_action_raises_value_error(self, client: TestClient):
        db, gen = _get_db()
        try:
            from app.models.user import User
            u = User(id="credit_unknown", email="unknown@test.com", full_name="Test", password_hash="x", credits=100)
            db.add(u)
            db.commit()
            svc = CreditService(db)
            with pytest.raises(ValueError, match="Unknown action"):
                svc.deduct_credits("credit_unknown", "nonexistent_action")
        finally:
            _close_db(db, gen)

    def test_user_not_found_on_deduct(self, client: TestClient):
        db, gen = _get_db()
        try:
            svc = CreditService(db)
            with pytest.raises(ValueError, match="User not found"):
                svc.deduct_credits("nonexistent-user-id", "ai_ask")
        finally:
            _close_db(db, gen)

    def test_ai_service_connection_error_returns_502(self, client: TestClient):
        token, _ = _signup(client, "ai_conn_err")
        with patch.object(AIService, "_call_openai", side_effect=ValueError("Could not connect to AI service")):
            resp = client.post("/api/ai/tutor", json={"message": "Hi"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 502
        assert "connect" in resp.json()["detail"].lower()


class TestRateLimiting:

    def test_rate_limit_headers_present(self, client: TestClient):
        token, _ = _signup(client, "ratelimit_hdr")
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert "X-RateLimit-Limit" in resp.headers
        assert "X-RateLimit-Remaining" in resp.headers


class TestGenerateQuizEdgeCases:

    def test_num_questions_bounds(self, client: TestClient):
        token, _ = _signup(client, "quiz_bounds")
        resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra", "num_questions": 0}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422
        resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra", "num_questions": 21}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 422
        resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra", "num_questions": 20}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200

    def test_generate_quiz_invalid_json_response(self, client: TestClient):
        token, _ = _signup(client, "quiz_badjson")
        with patch.object(AIService, "_call_openai", return_value="not valid json"):
            resp = client.post("/api/ai/generate-quiz", json={"subject": "Math", "topic": "Algebra"}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Quiz on Algebra"
        assert data["questions"] == []
