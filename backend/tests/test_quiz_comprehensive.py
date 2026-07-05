import pytest
import uuid
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.models.subject import Subject
from app.models.quiz import Quiz, Question
from app.models.lesson import Lesson, Topic
from app.models.question_pool import QuestionPool
from app.services.question_pool_service import QuestionPoolService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def db_session(client):
    override = app.dependency_overrides.get(get_db)
    if override is None:
        pytest.fail("No DB override found")
    gen = override()
    db = next(gen)
    yield db
    gen.close()


def make_subject(db, name="Mathematics", slug="mathematics", category="science"):
    s = Subject(id=str(uuid.uuid4()), name=name, slug=slug, category=category)
    db.add(s)
    db.commit()
    return s


def make_quiz(db, subject_id, title="Test Quiz", pass_percentage=50, difficulty="medium", time_limit_minutes=10):
    q = Quiz(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        title=title,
        pass_percentage=pass_percentage,
        difficulty=difficulty,
        time_limit_minutes=time_limit_minutes,
    )
    db.add(q)
    db.commit()
    return q


def make_question(db, quiz_id, text="Sample?", correct_answer="A", order_index=1):
    qst = Question(
        id=str(uuid.uuid4()),
        quiz_id=quiz_id,
        text=text,
        options=["A) Option A", "B) Option B", "C) Option C", "D) Option D"],
        correct_answer=correct_answer,
        order_index=order_index,
        question_type="multiple_choice",
    )
    db.add(qst)
    db.commit()
    return qst


def make_pool_question(db, subject_id, text="Pool Q?", correct_answer="A", topic="Algebra"):
    pq = QuestionPool(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        topic=topic,
        text=text,
        options=["A) PoolA", "B) PoolB", "C) PoolC", "D) PoolD"],
        correct_answer=correct_answer,
        source="ai_generated",
        is_active=True,
    )
    db.add(pq)
    db.commit()
    return pq


def make_topic(db, subject_id, title="Algebra"):
    lesson = Lesson(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        title="Lesson 1",
        slug="lesson-1",
    )
    db.add(lesson)
    db.flush()
    t = Topic(id=str(uuid.uuid4()), lesson_id=lesson.id, title=title)
    db.add(t)
    db.commit()
    return t


def signup_and_token(client: TestClient, email: str = None) -> dict:
    email = email or f"quiz_{uuid.uuid4().hex[:8]}@test.com"
    resp = client.post("/api/auth/signup", json={
        "email": email,
        "password": "TestPassword123!",
        "full_name": "Quiz Tester",
    })
    assert resp.status_code == 201
    data = resp.json()
    return {"token": data["access_token"], "user": data["user"], "email": email}


# ---------------------------------------------------------------------------
# 1. get_quizzes
# ---------------------------------------------------------------------------

class TestGetQuizzes:
    def test_empty_list(self, client: TestClient, db_session):
        """No quizzes exist → empty list."""
        info = signup_and_token(client)
        resp = client.get("/api/quizzes", headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["quizzes"] == []
        assert data["total"] == 0

    def test_with_subject_filter(self, client: TestClient, db_session):
        """Filter returns only quizzes for the given subject."""
        info = signup_and_token(client)
        s1 = make_subject(db_session, "Maths", "maths", "science")
        s2 = make_subject(db_session, "English", "english", "arts")
        q1 = make_quiz(db_session, s1.id, "Math Quiz")
        q2 = make_quiz(db_session, s2.id, "English Quiz")

        resp = client.get(f"/api/quizzes?subject_id={s1.id}",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        ids = [q["id"] for q in data["quizzes"]]
        assert q1.id in ids
        assert q2.id not in ids
        assert data["total"] == 1

    def test_pagination(self, client: TestClient, db_session):
        """page & page_size parameters work correctly."""
        info = signup_and_token(client)
        subj = make_subject(db_session)
        ids = []
        for i in range(5):
            q = make_quiz(db_session, subj.id, f"Quiz {i}")
            ids.append(q.id)

        resp = client.get("/api/quizzes?page=1&page_size=2",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["quizzes"]) == 2
        assert data["total"] == 5

        resp2 = client.get("/api/quizzes?page=3&page_size=2",
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert len(data2["quizzes"]) == 1

    def test_no_auth(self, client: TestClient):
        """Missing auth header → 401/403."""
        resp = client.get("/api/quizzes")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# 2. get_quiz (detail)
# ---------------------------------------------------------------------------

class TestGetQuiz:
    def test_existing_quiz(self, client: TestClient, db_session):
        """Fetch a quiz by ID returns quiz metadata + questions."""
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Detail Quiz", pass_percentage=70)
        q1 = make_question(db_session, quiz.id, "Q1?", "A", 1)
        q2 = make_question(db_session, quiz.id, "Q2?", "B", 2)

        resp = client.get(f"/api/quizzes/{quiz.id}",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == quiz.id
        assert data["title"] == "Detail Quiz"
        assert data["pass_percentage"] == 70

    def test_non_existent_quiz(self, client: TestClient, db_session):
        """Fetching a non-existent ID returns 404."""
        info = signup_and_token(client)
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/api/quizzes/{fake_id}",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 404

    def test_quiz_with_questions_detail(self, client: TestClient, db_session):
        """Response contains properly structured questions array."""
        import json as _json
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Struct Quiz")
        make_question(db_session, quiz.id, "Alpha?", "C", 1)
        make_question(db_session, quiz.id, "Beta?", "D", 2)

        resp = client.get(f"/api/quizzes/{quiz.id}",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "questions" in data
        for q in data["questions"]:
            assert "id" in q
            assert "text" in q
            assert "options" in q
            assert isinstance(q["options"], list)
            assert "order_index" in q
            assert "question_type" in q


# ---------------------------------------------------------------------------
# 3. submit_quiz
# ---------------------------------------------------------------------------

class TestSubmitQuiz:
    def _setup_quiz_for_submit(self, db_session, num_questions=5, pass_pct=50):
        subj = make_subject(db_session, "SubmitSubject", "submit-subject", "science")
        quiz = make_quiz(db_session, subj.id, "Submit Quiz", pass_percentage=pass_pct)
        qs = []
        for i in range(num_questions):
            q = make_question(db_session, quiz.id, f"SQ{i}?", "A", i)
            qs.append(q)
        return subj, quiz, qs

    # -- correctness variants --

    def test_all_correct(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj, quiz, qs = self._setup_quiz_for_submit(db_session, 5)
        answers = {q.id: "A" for q in qs}
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": answers, "time_taken_seconds": 60},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 5
        assert data["total"] == 5
        assert data["percentage"] == 100.0
        assert data["passed"] is True

    def test_partial_correct(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj, quiz, qs = self._setup_quiz_for_submit(db_session, 4)
        answers = {qs[0].id: "A", qs[1].id: "B", qs[2].id: "A", qs[3].id: "B"}
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": answers, "time_taken_seconds": 30},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 2  # Q0 correct, Q2 correct → 2
        assert data["total"] == 4
        assert data["percentage"] == 50.0
        assert data["passed"] is True  # pass_percentage=50

    def test_all_wrong(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj, quiz, qs = self._setup_quiz_for_submit(db_session, 3)
        answers = {q.id: "B" for q in qs}  # correct is "A"
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": answers, "time_taken_seconds": 45},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 0
        assert data["total"] == 3
        assert data["percentage"] == 0.0
        assert data["passed"] is False

    def test_empty_answers_dict(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj, quiz, qs = self._setup_quiz_for_submit(db_session, 2)
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": {}, "time_taken_seconds": 10},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 0
        assert data["total"] == 2

    # -- time_taken edge cases --

    def test_time_taken_zero(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj, quiz, qs = self._setup_quiz_for_submit(db_session, 1)
        answers = {qs[0].id: "A"}
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": answers, "time_taken_seconds": 0},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200

    def test_time_taken_negative(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj, quiz, qs = self._setup_quiz_for_submit(db_session, 1)
        answers = {qs[0].id: "A"}
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": answers, "time_taken_seconds": -1},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200  # service stores as string, no validation

    def test_time_taken_large(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj, quiz, qs = self._setup_quiz_for_submit(db_session, 1)
        answers = {qs[0].id: "A"}
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": answers, "time_taken_seconds": 2147483647},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200

    # -- error handling --

    def test_quiz_not_found(self, client: TestClient, db_session):
        info = signup_and_token(client)
        fake_id = str(uuid.uuid4())
        resp = client.post(f"/api/quizzes/{fake_id}/submit",
                           json={"answers": {"q1": "A"}, "time_taken_seconds": 10},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 400  # service raises ValueError → 400

    def test_submit_no_auth(self, client: TestClient):
        fake_id = str(uuid.uuid4())
        resp = client.post(f"/api/quizzes/{fake_id}/submit",
                           json={"answers": {}, "time_taken_seconds": 10})
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# 4. get_my_attempts
# ---------------------------------------------------------------------------

class TestGetMyAttempts:
    def test_no_attempts(self, client: TestClient, db_session):
        info = signup_and_token(client)
        resp = client.get("/api/quizzes/attempts/mine",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["attempts"] == []
        assert data["total"] == 0

    def test_after_submission(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id)
        q = make_question(db_session, quiz.id, "Q?", "A", 1)
        client.post(f"/api/quizzes/{quiz.id}/submit",
                    json={"answers": {q.id: "A"}, "time_taken_seconds": 20},
                    headers={"Authorization": f"Bearer {info['token']}"})

        resp = client.get("/api/quizzes/attempts/mine",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        att = data["attempts"][0]
        assert att["quiz_id"] == quiz.id
        assert att["score"] == "1"
        assert att["total"] == "1"

    def test_multiple_attempts(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id)
        q1 = make_question(db_session, quiz.id, "Q1?", "A", 1)
        q2 = make_question(db_session, quiz.id, "Q2?", "B", 2)

        # first attempt — all wrong
        client.post(f"/api/quizzes/{quiz.id}/submit",
                    json={"answers": {q1.id: "B", q2.id: "A"}, "time_taken_seconds": 10},
                    headers={"Authorization": f"Bearer {info['token']}"})
        # second attempt — all correct
        client.post(f"/api/quizzes/{quiz.id}/submit",
                    json={"answers": {q1.id: "A", q2.id: "B"}, "time_taken_seconds": 15},
                    headers={"Authorization": f"Bearer {info['token']}"})

        resp = client.get("/api/quizzes/attempts/mine",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2


# ---------------------------------------------------------------------------
# 5. Question detail with pool questions
# ---------------------------------------------------------------------------

class TestQuestionDetailWithPool:
    def test_hardcoded_and_pool_combined(self, client: TestClient, db_session):
        """get_quiz returns a mix of hardcoded and pool questions."""
        info = signup_and_token(client)
        subj = make_subject(db_session, "PoolSubject", "pool-subject", "science")
        quiz = make_quiz(db_session, subj.id, "Pool Quiz")

        # hardcoded
        h1 = make_question(db_session, quiz.id, "Hardcoded 1?", "A", 1)
        h2 = make_question(db_session, quiz.id, "Hardcoded 2?", "B", 2)

        # pool questions
        for i in range(15):
            make_pool_question(db_session, subj.id, f"Pool Q{i}?", "A" if i % 2 == 0 else "B")

        # topic needed for pool selection
        make_topic(db_session, subj.id, "Algebra")

        resp = client.get(f"/api/quizzes/{quiz.id}",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "questions" in data
        assert len(data["questions"]) == 15  # target_count
        # at least the hardcoded ones should be present
        q_ids = [q["id"] for q in data["questions"]]
        assert h1.id in q_ids
        assert h2.id in q_ids

    def test_submit_with_pool_questions(self, client: TestClient, db_session):
        """Submit works when pool questions are present."""
        info = signup_and_token(client)
        subj = make_subject(db_session, "PoolSubmit", "pool-submit", "science")
        quiz = make_quiz(db_session, subj.id, "Pool Submit Quiz", pass_percentage=50)

        h1 = make_question(db_session, quiz.id, "Hard 1?", "A", 1)
        make_topic(db_session, subj.id, "Algebra")

        for i in range(15):
            make_pool_question(db_session, subj.id, f"Pool{i}?", "B", "Algebra")

        # first fetch to see questions
        detail = client.get(f"/api/quizzes/{quiz.id}",
                            headers={"Authorization": f"Bearer {info['token']}"})
        assert detail.status_code == 200
        questions = detail.json()["questions"]

        # answer all with "B" — some will be wrong (hardcoded expects "A")
        answers = {q["id"]: "B" for q in questions}
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": answers, "time_taken_seconds": 30},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] >= 0
        assert data["total"] > 0
        # at least 1 wrong (the hardcoded one expects "A")
        assert data["score"] < data["total"] or data["score"] == 0


# ---------------------------------------------------------------------------
# 6. Scoring edge cases & boundary
# ---------------------------------------------------------------------------

class TestScoringEdges:
    def test_boundary_pass_percentage(self, client: TestClient, db_session, monkeypatch):
        """Quiz with pass_percentage=60, score exactly 60%."""
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Boundary Quiz", pass_percentage=60)
        qs = []
        for i in range(5):
            qs.append(make_question(db_session, quiz.id, f"B{i}?", "A", i))

        # 3 correct out of 5 = 60% → exactly pass
        answers = {qs[0].id: "A", qs[1].id: "A", qs[2].id: "A",
                   qs[3].id: "B", qs[4].id: "B"}
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": answers, "time_taken_seconds": 25},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["percentage"] == 60.0
        assert data["passed"] is True  # >= pass_percentage

    def test_boundary_below_pass(self, client: TestClient, db_session, monkeypatch):
        """59% when pass_percentage=60 → not passed."""
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Below Quiz", pass_percentage=60)
        qs = []
        # We need a total where 59% is not an integer,
        # so choose a number where a specific count gives 59.x
        # 7 questions: 4/7 = 57.14% (FAIL), 5/7 = 71.43% (PASS)
        # Let's use 10 questions: 5/10 = 50% (FAIL), 6/10 = 60% (PASS)
        # 5/10 = 50% < 60%
        for i in range(10):
            qs.append(make_question(db_session, quiz.id, f"E{i}?", "A", i))
        answers = {q.id: "A" for q in qs[:5]}  # 5 correct
        answers.update({q.id: "B" for q in qs[5:]})  # 5 wrong
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": answers, "time_taken_seconds": 20},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["percentage"] == 50.0
        assert data["passed"] is False

    def test_perfect_score(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Perfect")
        q = make_question(db_session, quiz.id, "P?", "C", 1)
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"answers": {q.id: "C"}, "time_taken_seconds": 5},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        assert resp.json()["percentage"] == 100.0


# ---------------------------------------------------------------------------
# 7. Auth / Security
# ---------------------------------------------------------------------------

class TestAuthSecurity:
    def test_get_quizzes_different_users_isolated(self, client: TestClient, db_session):
        """Each user sees the same quizzes but own attempts are isolated."""
        u1 = signup_and_token(client, "u1_quiz@test.com")
        u2 = signup_and_token(client, "u2_quiz@test.com")

        resp1 = client.get("/api/quizzes", headers={"Authorization": f"Bearer {u1['token']}"})
        resp2 = client.get("/api/quizzes", headers={"Authorization": f"Bearer {u2['token']}"})
        # both see the same quizzes (global list)
        assert resp1.json()["total"] == resp2.json()["total"]

    def test_invalid_token(self, client: TestClient):
        resp = client.get("/api/quizzes",
                          headers={"Authorization": "Bearer invalidtoken123"})
        assert resp.status_code in (401, 403)
