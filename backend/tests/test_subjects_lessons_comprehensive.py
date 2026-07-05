import uuid
import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.services.ai_service import AIService


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
        "email": f"sl_{tag}@example.com",
        "password": "TestPassword123!",
        "full_name": "SL Test User",
    })
    assert resp.status_code == 201
    return resp.json()["access_token"]


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
        u = db.query(User).filter(User.id == user_id).first()
        if u:
            u.credits = amount
            db.commit()
    finally:
        _close_db(db, gen)


def _seed_data():
    from app.models.subject import Subject
    from app.models.lesson import Lesson, Topic
    data = {
        "subj_id": str(uuid.uuid4()),
        "subj2_id": str(uuid.uuid4()),
        "lesson1_id": str(uuid.uuid4()),
        "lesson2_id": str(uuid.uuid4()),
        "topic1_id": str(uuid.uuid4()),
        "topic2_id": str(uuid.uuid4()),
    }
    db, gen = _get_db()
    try:
        s1 = Subject(id=data["subj_id"], name="Mathematics", slug="mathematics", description="Numbers", category="science", icon="calc", color="#ff0000", order_index=1)
        s2 = Subject(id=data["subj2_id"], name="English", slug="english", description="Language", category="arts", icon="book", color="#00ff00", order_index=2)
        l1 = Lesson(id=data["lesson1_id"], subject_id=data["subj_id"], title="Algebra", slug="algebra", content="Lesson content", summary="Algebra summary", order_index=1, estimated_minutes=30)
        l2 = Lesson(id=data["lesson2_id"], subject_id=data["subj_id"], title="Geometry", slug="geometry", content="Geo content", summary="Geometry summary", order_index=2, estimated_minutes=45)
        t1 = Topic(id=data["topic1_id"], lesson_id=data["lesson1_id"], title="Variables", content="Short intro to variables", order_index=1)
        t2 = Topic(id=data["topic2_id"], lesson_id=data["lesson1_id"], title="Equations", content="E" * 3000, order_index=2)
        db.add_all([s1, s2, l1, l2, t1, t2])
        db.commit()
    finally:
        _close_db(db, gen)
    return data


class TestGetSubjects:

    def test_empty_subjects(self, client: TestClient):
        token = _signup(client, "subj_empty")
        resp = client.get("/api/subjects", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["subjects"] == []

    def test_with_subjects(self, client: TestClient):
        _seed_data()
        token = _signup(client, "subj_list")
        resp = client.get("/api/subjects", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["subjects"]) == 2
        assert {s["name"] for s in data["subjects"]} == {"Mathematics", "English"}

    def test_filter_by_category(self, client: TestClient):
        _seed_data()
        token = _signup(client, "subj_cat")
        resp = client.get("/api/subjects?category=arts", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["subjects"]) == 1
        assert data["subjects"][0]["name"] == "English"

    def test_unauthorized(self, client: TestClient):
        resp = client.get("/api/subjects")
        assert resp.status_code in (401, 403)

    def test_subject_fields_structure(self, client: TestClient):
        _seed_data()
        token = _signup(client, "subj_fields")
        resp = client.get("/api/subjects", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        subjects = resp.json()["subjects"]
        assert len(subjects) > 0
        expected_fields = {"id", "name", "slug", "description", "category", "icon", "color"}
        for s in subjects:
            assert expected_fields.issubset(s.keys())
            assert s["name"]
            assert s["slug"]
            assert s["category"]
            assert s["id"]


class TestGetSubjectBySlug:

    def test_existing(self, client: TestClient):
        _seed_data()
        token = _signup(client, "subjslug_exist")
        resp = client.get("/api/subjects/mathematics", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["name"] == "Mathematics"

    def test_not_found(self, client: TestClient):
        token = _signup(client, "subjslug_nf")
        resp = client.get("/api/subjects/nonexistent", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_unauthorized(self, client: TestClient):
        resp = client.get("/api/subjects/mathematics")
        assert resp.status_code in (401, 403)


class TestGetLessons:

    def test_existing_subject(self, client: TestClient):
        _seed_data()
        token = _signup(client, "less_exist")
        resp = client.get("/api/subjects/mathematics/lessons", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["lessons"]) == 2
        assert {l["slug"] for l in data["lessons"]} == {"algebra", "geometry"}

    def test_subject_not_found(self, client: TestClient):
        token = _signup(client, "less_nf")
        resp = client.get("/api/subjects/nonexistent/lessons", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_subject_with_no_lessons(self, client: TestClient):
        _seed_data()
        token = _signup(client, "less_empty")
        resp = client.get("/api/subjects/english/lessons", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["lessons"] == []

    def test_order_index_verified(self, client: TestClient):
        _seed_data()
        token = _signup(client, "less_order")
        resp = client.get("/api/subjects/mathematics/lessons", headers={"Authorization": f"Bearer {token}"})
        orders = [l["order_index"] for l in resp.json()["lessons"]]
        assert orders == sorted(orders)

    def test_unauthorized(self, client: TestClient):
        resp = client.get("/api/subjects/mathematics/lessons")
        assert resp.status_code in (401, 403)


class TestGetLessonDetail:

    def test_existing(self, client: TestClient):
        _seed_data()
        token = _signup(client, "ldetail_exist")
        resp = client.get("/api/subjects/mathematics/lessons/algebra", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Algebra"
        assert data["summary"] == "Algebra summary"
        assert data["estimated_minutes"] == 30

    def test_lesson_not_found(self, client: TestClient):
        token = _signup(client, "ldetail_nf")
        resp = client.get("/api/subjects/mathematics/lessons/nonexistent", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_wrong_subject(self, client: TestClient):
        _seed_data()
        token = _signup(client, "ldetail_wrong")
        resp = client.get("/api/subjects/english/lessons/algebra", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_subject_not_found(self, client: TestClient):
        token = _signup(client, "ldetail_subjnf")
        resp = client.get("/api/subjects/nonexistent/lessons/algebra", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_topics_included(self, client: TestClient):
        _seed_data()
        token = _signup(client, "ldetail_topics")
        resp = client.get("/api/subjects/mathematics/lessons/algebra", headers={"Authorization": f"Bearer {token}"})
        topics = resp.json()["topics"]
        assert {t["title"] for t in topics} == {"Variables", "Equations"}

    def test_content_type_basic_vs_ai_expanded(self, client: TestClient):
        _seed_data()
        token = _signup(client, "ldetail_ctype")
        resp = client.get("/api/subjects/mathematics/lessons/algebra", headers={"Authorization": f"Bearer {token}"})
        ctypes = {t["title"]: t["content_type"] for t in resp.json()["topics"]}
        assert ctypes["Variables"] == "basic"
        assert ctypes["Equations"] == "ai_expanded"


class TestGetTopicDetail:

    def test_existing(self, client: TestClient):
        d = _seed_data()
        token = _signup(client, "tdetail_exist")
        resp = client.get(f"/api/subjects/mathematics/topics/{d['topic1_id']}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Variables"
        assert data["has_expanded"] is False
        assert data["lesson"]["slug"] == "algebra"
        assert data["subject"]["name"] == "Mathematics"

    def test_expanded_topic_flagged(self, client: TestClient):
        d = _seed_data()
        token = _signup(client, "tdetail_expanded")
        resp = client.get(f"/api/subjects/mathematics/topics/{d['topic2_id']}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["has_expanded"] is True

    def test_not_found(self, client: TestClient):
        token = _signup(client, "tdetail_nf")
        resp = client.get("/api/subjects/mathematics/topics/nonexistent-id", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_topic_not_in_subject(self, client: TestClient):
        d = _seed_data()
        token = _signup(client, "tdetail_wrongsubj")
        resp = client.get(f"/api/subjects/english/topics/{d['topic1_id']}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_all_topics_included(self, client: TestClient):
        d = _seed_data()
        token = _signup(client, "tdetail_alltopics")
        resp = client.get(f"/api/subjects/mathematics/topics/{d['topic1_id']}", headers={"Authorization": f"Bearer {token}"})
        assert len(resp.json()["all_topics"]) == 2


class TestExpandTopicContent:

    MOCK_EXPANDED = "<h2>Expanded Content</h2><p>Full textbook chapter data.</p>"

    @pytest.fixture(autouse=True)
    def _mock_ai(self):
        with patch.object(AIService, "generate_textbook_content", return_value=self.MOCK_EXPANDED):
            yield

    def test_first_expansion(self, client: TestClient):
        d = _seed_data()
        token = _signup(client, "expand_first")
        db, gen = _get_db()
        try:
            from app.models.user import User
            u = db.query(User).filter(User.email == "sl_expand_first@example.com").first()
            u.credits = 10
            db.commit()
        finally:
            _close_db(db, gen)

        resp = client.post(f"/api/subjects/mathematics/topics/{d['topic1_id']}/expand", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["expanded"] is True
        assert data["subject"] == "Mathematics"
        assert data["topic"] == "Variables"

    def test_already_expanded_returns_updated(self, client: TestClient):
        d = _seed_data()
        token = _signup(client, "expand_again")
        db, gen = _get_db()
        try:
            from app.models.user import User
            u = db.query(User).filter(User.email == "sl_expand_again@example.com").first()
            u.credits = 10
            db.commit()
        finally:
            _close_db(db, gen)

        resp = client.post(f"/api/subjects/mathematics/topics/{d['topic2_id']}/expand", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["expanded"] is True

    def test_credit_deduction_failure(self, client: TestClient):
        d = _seed_data()
        token = _signup(client, "expand_nocred")
        db, gen = _get_db()
        try:
            from app.models.user import User
            u = db.query(User).filter(User.email == "sl_expand_nocred@example.com").first()
            u.credits = 0
            db.commit()
        finally:
            _close_db(db, gen)

        resp = client.post(f"/api/subjects/mathematics/topics/{d['topic1_id']}/expand", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 402

    def test_subject_not_found(self, client: TestClient):
        d = _seed_data()
        token = _signup(client, "expand_subjnf")
        resp = client.post(f"/api/subjects/nonexistent/topics/{d['topic1_id']}/expand", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_topic_not_found(self, client: TestClient):
        _seed_data()
        token = _signup(client, "expand_topicnf")
        resp = client.post("/api/subjects/mathematics/topics/nonexistent/expand", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 404

    def test_unauthorized(self, client: TestClient):
        d = _seed_data()
        resp = client.post(f"/api/subjects/mathematics/topics/{d['topic1_id']}/expand")
        assert resp.status_code in (401, 403)


class TestEdgeCases:

    def test_subject_missing_optional_fields(self, client: TestClient):
        from app.models.subject import Subject
        db, gen = _get_db()
        try:
            sparse = Subject(id=str(uuid.uuid4()), name="Physics", slug="physics", category="science")
            db.add(sparse)
            db.commit()
        finally:
            _close_db(db, gen)

        token = _signup(client, "edge_sparse")
        resp = client.get("/api/subjects/physics", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["icon"] is None
        assert resp.json()["color"] is None

    def test_lesson_without_content(self, client: TestClient):
        d = _seed_data()
        from app.models.lesson import Lesson
        db, gen = _get_db()
        try:
            empty = Lesson(id=str(uuid.uuid4()), subject_id=d["subj_id"], title="Empty", slug="empty-lesson", order_index=3)
            db.add(empty)
            db.commit()
        finally:
            _close_db(db, gen)

        token = _signup(client, "edge_nocont")
        resp = client.get(f"/api/subjects/mathematics/lessons/empty-lesson", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["content"] is None
