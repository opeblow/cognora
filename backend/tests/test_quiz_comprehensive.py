import pytest
import uuid
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.models.subject import Subject
from app.models.quiz import Quiz
from app.models.lesson import Lesson, Topic
from app.services.quiz_service import QuizService


async def _mock_generate_questions(self, subject_name, topics, count):
    """Return fake controlled questions so AI is never called in tests."""
    return [
        {
            "id": str(uuid.uuid4()),
            "text": f"Test Question {i}?",
            "options": ["A) Option A", "B) Option B", "C) Option C", "D) Option D"],
            "correct_answer": "A) Option A",
            "explanation": f"Explanation for Q{i}",
            "difficulty": "hard",
            "question_type": "multiple_choice",
        }
        for i in range(count)
    ]


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


def start_quiz_and_get_session(client, token, quiz_id):
    """Start a quiz (which generates Qs + creates a session) and return session_id + first question id."""
    resp = client.get(f"/api/quizzes/{quiz_id}",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    return data["session_id"], data["questions"]


# ---------------------------------------------------------------------------
# 1. get_quizzes
# ---------------------------------------------------------------------------

class TestGetQuizzes:
    def test_empty_list(self, client: TestClient, db_session):
        info = signup_and_token(client)
        resp = client.get("/api/quizzes", headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["quizzes"] == []
        assert data["total"] == 0

    def test_with_subject_filter(self, client: TestClient, db_session):
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
        resp = client.get("/api/quizzes")
        assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# 2. get_quiz (detail)
# ---------------------------------------------------------------------------

class TestGetQuiz:
    def test_existing_quiz(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Detail Quiz", pass_percentage=70)

        resp = client.get(f"/api/quizzes/{quiz.id}",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == quiz.id
        assert data["title"] == "Detail Quiz"
        assert data["pass_percentage"] == 70
        assert "session_id" in data
        assert data["question_count"] == 60

    def test_non_existent_quiz(self, client: TestClient, db_session):
        info = signup_and_token(client)
        fake_id = str(uuid.uuid4())
        resp = client.get(f"/api/quizzes/{fake_id}",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 404

    def test_quiz_with_questions_detail(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Struct Quiz")

        resp = client.get(f"/api/quizzes/{quiz.id}",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "questions" in data
        assert len(data["questions"]) == 60
        for q in data["questions"]:
            assert "id" in q
            assert "text" in q
            assert "options" in q
            assert isinstance(q["options"], list)
            assert "order_index" in q
            assert "question_type" in q
            # must NOT leak correct_answer or explanation to frontend
            assert "correct_answer" not in q
            assert "explanation" not in q


# ---------------------------------------------------------------------------
# 3. submit_quiz
# ---------------------------------------------------------------------------

class TestSubmitQuiz:
    def _setup_quiz_for_submit(self, db_session, num_questions=5, pass_pct=50):
        subj = make_subject(db_session, "SubmitSubject", "submit-subject", "science")
        quiz = make_quiz(db_session, subj.id, "Submit Quiz", pass_percentage=pass_pct)
        return subj, quiz

    def test_all_correct(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj, quiz = self._setup_quiz_for_submit(db_session, 5)
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)

        answers = {q["id"]: "A) Option A" for q in questions}  # all correct = A
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": answers, "time_taken_seconds": 60},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 60
        assert data["total"] == 60
        assert data["percentage"] == 100.0
        assert data["passed"] is True

    def test_partial_correct(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj, quiz = self._setup_quiz_for_submit(db_session, 4)
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)

        # Only answer first half correctly, second half with wrong answer
        answers = {}
        for i, q in enumerate(questions):
            if i < 30:
                answers[q["id"]] = "A) Option A"  # correct
            else:
                answers[q["id"]] = "B) Option B"  # wrong (correct is A)
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": answers, "time_taken_seconds": 30},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 30
        assert data["total"] == 60
        assert data["percentage"] == 50.0

    def test_all_wrong(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj, quiz = self._setup_quiz_for_submit(db_session, 3)
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)

        answers = {q["id"]: "B) Option B" for q in questions}  # all wrong (correct is A)
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": answers, "time_taken_seconds": 45},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 0
        assert data["total"] == 60
        assert data["percentage"] == 0.0
        assert data["passed"] is False

    def test_empty_answers_dict(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj, quiz = self._setup_quiz_for_submit(db_session, 2)
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)

        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": {}, "time_taken_seconds": 10},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 0
        assert data["total"] == 60

    def test_time_taken_zero(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj, quiz = self._setup_quiz_for_submit(db_session, 1)
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)
        answers = {questions[0]["id"]: "A) Option A"}

        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": answers, "time_taken_seconds": 0},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 1

    def test_large_time_taken(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj, quiz = self._setup_quiz_for_submit(db_session, 2)
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)
        answers = {q["id"]: "A) Option A" for q in questions}

        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": answers, "time_taken_seconds": 99999},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200

    def test_quiz_not_found(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj, quiz = self._setup_quiz_for_submit(db_session, 1)
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)

        fake_quiz_id = str(uuid.uuid4())
        resp = client.post(f"/api/quizzes/{fake_quiz_id}/submit",
                           json={"session_id": session_id, "answers": {}, "time_taken_seconds": 5},
                           headers={"Authorization": f"Bearer {info['token']}"})
        # Quiz ID is not validated on submit — session_id is what matters,
        # so it should succeed as long as the session exists.
        assert resp.status_code == 200

    def test_no_auth_submit(self, client: TestClient):
        resp = client.post("/api/quizzes/some-id/submit",
                           json={"session_id": "x", "answers": {}, "time_taken_seconds": 5})
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

    def test_after_submit_one(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "My Attempt Quiz")
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)
        answers = {q["id"]: "A) Option A" for q in questions}
        client.post(f"/api/quizzes/{quiz.id}/submit",
                    json={"session_id": session_id, "answers": answers, "time_taken_seconds": 20},
                    headers={"Authorization": f"Bearer {info['token']}"})

        resp = client.get("/api/quizzes/attempts/mine",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        a = data["attempts"][0]
        assert a["quiz_id"] == quiz.id
        assert a["score"] == "60"

    def test_multiple_attempts(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj = make_subject(db_session)
        q1 = make_quiz(db_session, subj.id, "Quiz 1")
        q2 = make_quiz(db_session, subj.id, "Quiz 2")

        for q in [q1, q2]:
            sid, qs = start_quiz_and_get_session(client, info["token"], q.id)
            client.post(f"/api/quizzes/{q.id}/submit",
                        json={"session_id": sid, "answers": {}, "time_taken_seconds": 5},
                        headers={"Authorization": f"Bearer {info['token']}"})

        resp = client.get("/api/quizzes/attempts/mine",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        assert resp.json()["total"] == 2


# ---------------------------------------------------------------------------
# 5. Scoring edges
# ---------------------------------------------------------------------------

class TestScoringEdges:
    def test_boundary_pass(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Boundary Quiz", pass_percentage=50)
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)

        half = len(questions) // 2
        answers = {}
        for i, q in enumerate(questions):
            answers[q["id"]] = "A) Option A" if i < half else "B) Option B"

        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": answers, "time_taken_seconds": 30},
                           headers={"Authorization": f"Bearer {info['token']}"})
        data = resp.json()
        # 30/60 = 50% → exactly at pass_percentage, should pass
        assert data["passed"] is True

    def test_boundary_fail(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Fail Quiz", pass_percentage=50)
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)

        below_half = (len(questions) // 2) - 1
        answers = {}
        for i, q in enumerate(questions):
            answers[q["id"]] = "A) Option A" if i < below_half else "B) Option B"

        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": answers, "time_taken_seconds": 30},
                           headers={"Authorization": f"Bearer {info['token']}"})
        data = resp.json()
        assert data["passed"] is False

    def test_perfect_score(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Perfect Quiz")
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)

        answers = {q["id"]: "A) Option A" for q in questions}
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": answers, "time_taken_seconds": 15},
                           headers={"Authorization": f"Bearer {info['token']}"})
        data = resp.json()
        assert data["score"] == 60
        assert data["percentage"] == 100.0
        assert data["passed"] is True


# ---------------------------------------------------------------------------
# 6. Auth & security
# ---------------------------------------------------------------------------

class TestAuthSecurity:
    def test_user_isolation(self, client: TestClient, db_session, monkeypatch):
        """User B cannot submit answers for User A's session."""
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info_a = signup_and_token(client, "user_a@test.com")
        info_b = signup_and_token(client, "user_b@test.com")

        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Isolation Quiz")
        session_id, questions = start_quiz_and_get_session(client, info_a["token"], quiz.id)
        answers = {questions[0]["id"]: "A) Option A"}

        # User B tries to submit with User A's session_id
        resp = client.post(f"/api/quizzes/{quiz.id}/submit",
                           json={"session_id": session_id, "answers": answers, "time_taken_seconds": 5},
                           headers={"Authorization": f"Bearer {info_b['token']}"})
        assert resp.status_code == 400  # session not found for user B

    def test_double_submit_blocks(self, client: TestClient, db_session, monkeypatch):
        """Submitting the same session twice is blocked."""
        monkeypatch.setattr(QuizService, "_generate_questions_for_session", _mock_generate_questions)
        info = signup_and_token(client)
        subj = make_subject(db_session)
        quiz = make_quiz(db_session, subj.id, "Double Submit")
        session_id, questions = start_quiz_and_get_session(client, info["token"], quiz.id)
        answers = {questions[0]["id"]: "A) Option A"}

        resp1 = client.post(f"/api/quizzes/{quiz.id}/submit",
                            json={"session_id": session_id, "answers": answers, "time_taken_seconds": 5},
                            headers={"Authorization": f"Bearer {info['token']}"})
        assert resp1.status_code == 200

        resp2 = client.post(f"/api/quizzes/{quiz.id}/submit",
                            json={"session_id": session_id, "answers": answers, "time_taken_seconds": 5},
                            headers={"Authorization": f"Bearer {info['token']}"})
        assert resp2.status_code == 400
        assert "already been submitted" in resp2.json()["detail"]
