import pytest
import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.models.subject import Subject
from app.models.user import User
from app.models.quiz import Quiz, Question, QuizAttempt, QuizAnswer
from app.models.exam import Exam, ExamResult
from app.models.progress import UserProgress
from app.models.analytics import UserAnalytics
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


def make_user(db, email=None):
    """Create a bare User directly (no auth flow) for analytics data setup."""
    from app.core.security import hash_password
    u = User(
        id=str(uuid.uuid4()),
        email=email or f"analytics_{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Analytics Tester",
        credits=50,
        is_verified=True,
        is_active=True,
    )
    db.add(u)
    db.commit()
    return u


def make_subject(db, name="Mathematics", slug="mathematics", category="science"):
    s = Subject(id=str(uuid.uuid4()), name=name, slug=slug, category=category)
    db.add(s)
    db.commit()
    return s


def make_progress(db, user_id, subject_id, lessons_completed=0, quizzes_taken=0,
                  average_score=0.0, study_time=0):
    p = UserProgress(
        id=str(uuid.uuid4()),
        user_id=user_id,
        subject_id=subject_id,
        lessons_completed=str(lessons_completed),
        quizzes_taken=str(quizzes_taken),
        average_score=str(average_score),
        total_study_time_minutes=str(study_time),
    )
    db.add(p)
    db.commit()
    return p


def make_quiz_attempt(db, user_id, subject_id, percentage=50.0,
                      completed_at=None, time_taken=60):
    """Create a Quiz, Question, and QuizAttempt with an answer."""
    quiz = Quiz(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        title="Analytics Quiz",
        pass_percentage=50,
    )
    db.add(quiz)
    db.flush()

    question = Question(
        id=str(uuid.uuid4()),
        quiz_id=quiz.id,
        text="Test Q?",
        options=["A) A", "B) B", "C) C", "D) D"],
        correct_answer="A",
        order_index=1,
    )
    db.add(question)
    db.flush()

    attempt = QuizAttempt(
        id=str(uuid.uuid4()),
        quiz_id=quiz.id,
        user_id=user_id,
        score=str(int(percentage * 1 / 100)) if percentage > 0 else "0",
        total="1",
        percentage=str(percentage),
        time_taken_seconds=str(time_taken),
        completed_at=completed_at or datetime.now(timezone.utc),
    )
    db.add(attempt)
    db.flush()

    answer = QuizAnswer(
        id=str(uuid.uuid4()),
        attempt_id=attempt.id,
        question_id=question.id,
        selected_answer="A",
        is_correct=percentage >= 50,
    )
    db.add(answer)
    db.commit()
    return attempt


def make_exam_result(db, user_id, exam, percentage=50.0, completed_at=None,
                     status="completed", time_taken=120):
    r = ExamResult(
        id=str(uuid.uuid4()),
        exam_id=exam.id,
        user_id=user_id,
        score=str(int(percentage * 1 / 100)) if percentage > 0 else "0",
        total="1",
        percentage=str(percentage),
        time_taken_seconds=str(time_taken),
        status=status,
        completed_at=completed_at or datetime.now(timezone.utc),
    )
    db.add(r)
    db.commit()
    return r


def signup_and_token(client: TestClient, email: str = None) -> dict:
    email = email or f"an_{uuid.uuid4().hex[:8]}@test.com"
    resp = client.post("/api/auth/signup", json={
        "email": email,
        "password": "TestPassword123!",
        "full_name": "Analytics Tester",
    })
    assert resp.status_code == 201
    data = resp.json()
    return {"token": data["access_token"], "user": data["user"], "email": email}


# ---------------------------------------------------------------------------
# 1. get_dashboard
# ---------------------------------------------------------------------------

class TestGetDashboard:
    def test_empty_data(self, client: TestClient, db_session):
        """Fresh user with no progress sees valid default dashboard."""
        info = signup_and_token(client)
        resp = client.get("/api/analytics/dashboard",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "welcome_name" in data
        assert data["welcome_name"] == "Analytics"
        assert "credits" in data
        assert "learning_streak" in data
        assert data["subject_stats"] == []
        assert data["progress_overview"] == []

    def test_with_progress_data(self, client: TestClient, db_session):
        """Dashboard returns subject stats based on progress records."""
        info = signup_and_token(client)
        user_id = info["user"]["id"]
        subj = make_subject(db_session, "Maths", "maths", "science")
        make_progress(db_session, user_id, subj.id, lessons_completed=5, quizzes_taken=3,
                      average_score=75.0, study_time=120)

        resp = client.get("/api/analytics/dashboard",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["subject_stats"]) == 1
        stats = data["subject_stats"][0]
        assert stats["subject_name"] == "Maths"
        assert stats["lessons_completed"] == 5
        assert stats["quizzes_taken"] == 3
        assert stats["average_score"] == 75.0
        assert stats["total_study_time_minutes"] == 120

    def test_progress_overview_matches_subject_stats(self, client: TestClient, db_session):
        """progress_overview and subject_stats should be the same list."""
        info = signup_and_token(client)
        user_id = info["user"]["id"]
        subj = make_subject(db_session, "Physics", "physics", "science")
        make_progress(db_session, user_id, subj.id, average_score=80.0)

        resp = client.get("/api/analytics/dashboard",
                          headers={"Authorization": f"Bearer {info['token']}"})
        data = resp.json()
        assert len(data["progress_overview"]) == len(data["subject_stats"]) == 1
        assert data["progress_overview"][0]["subject_id"] == data["subject_stats"][0]["subject_id"]


# ---------------------------------------------------------------------------
# 2. get_overview (analytics overview)
# ---------------------------------------------------------------------------

class TestGetOverview:
    def test_empty_state(self, client: TestClient, db_session):
        """Analytics overview with no data returns zeros."""
        info = signup_and_token(client)
        resp = client.get("/api/analytics/overview",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_quizzes_taken"] == 0
        assert data["total_exams_taken"] == 0
        assert data["overall_average"] == 0.0
        assert data["learning_streak"] == 0
        assert data["total_study_time_minutes"] == 0
        assert data["accuracy_trends"] == []
        assert data["improvement_rate"] == 0.0
        assert data["topic_mastery"] == []
        assert data["strong_subjects"] == []
        assert data["weak_subjects"] == []

    def test_with_quiz_and_exam_data(self, client: TestClient, db_session, monkeypatch):
        """Overview aggregates quiz and exam results."""
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        user_id = info["user"]["id"]

        subj1 = make_subject(db_session, "Maths", "maths", "science")
        subj2 = make_subject(db_session, "English", "english", "arts")

        # Progress records
        make_progress(db_session, user_id, subj1.id, average_score=80.0, study_time=60)
        make_progress(db_session, user_id, subj2.id, average_score=60.0, study_time=30)

        # Quiz attempts
        make_quiz_attempt(db_session, user_id, subj1.id, percentage=80.0,
                          completed_at=datetime.now(timezone.utc) - timedelta(days=2))
        make_quiz_attempt(db_session, user_id, subj2.id, percentage=60.0,
                          completed_at=datetime.now(timezone.utc) - timedelta(days=1))

        # Exam
        exam = Exam(id=str(uuid.uuid4()), subject_id=subj1.id, title="Test Exam",
                    exam_type="JAMB")
        db_session.add(exam)
        db_session.commit()
        make_exam_result(db_session, user_id, exam, percentage=70.0)

        resp = client.get("/api/analytics/overview",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_quizzes_taken"] == 2
        assert data["total_exams_taken"] == 1
        # (80+60+70) / 3 = 70.0
        assert data["overall_average"] == 70.0
        assert data["total_study_time_minutes"] == 90


# ---------------------------------------------------------------------------
# 3. accuracy_trends
# ---------------------------------------------------------------------------

class TestAccuracyTrends:
    def test_no_data(self, client: TestClient, db_session):
        info = signup_and_token(client)
        resp = client.get("/api/analytics/accuracy-trends",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["trends"] == []

    def test_single_entry(self, client: TestClient, db_session):
        info = signup_and_token(client)
        user_id = info["user"]["id"]
        subj = make_subject(db_session)
        make_quiz_attempt(db_session, user_id, subj.id, percentage=85.0)

        resp = client.get("/api/analytics/accuracy-trends",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["trends"]) == 1
        assert data["trends"][0]["quiz_score"] == 85.0

    def test_multiple_entries(self, client: TestClient, db_session):
        info = signup_and_token(client)
        user_id = info["user"]["id"]
        subj = make_subject(db_session)

        now = datetime.now(timezone.utc)
        make_quiz_attempt(db_session, user_id, subj.id, percentage=50.0,
                          completed_at=now - timedelta(days=5))
        make_quiz_attempt(db_session, user_id, subj.id, percentage=70.0,
                          completed_at=now - timedelta(days=3))
        make_quiz_attempt(db_session, user_id, subj.id, percentage=90.0,
                          completed_at=now - timedelta(days=1))

        resp = client.get("/api/analytics/accuracy-trends",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["trends"]) == 3
        scores = [t["quiz_score"] for t in data["trends"]]
        assert scores == sorted(scores)  # ascending order


# ---------------------------------------------------------------------------
# 4. topic_mastery
# ---------------------------------------------------------------------------

class TestTopicMastery:
    def test_empty(self, client: TestClient, db_session):
        info = signup_and_token(client)
        resp = client.get("/api/analytics/topic-mastery",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["mastery"] == []

    def test_with_quiz_performance(self, client: TestClient, db_session, monkeypatch):
        """Topic mastery reflects quiz scores for a subject."""
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        user_id = info["user"]["id"]
        subj = make_subject(db_session, "Chemistry", "chemistry", "science")

        # Progress is needed for topic_mastery to iterate
        make_progress(db_session, user_id, subj.id, lessons_completed=10)

        # Quiz attempts for this subject
        make_quiz_attempt(db_session, user_id, subj.id, percentage=70.0,
                          completed_at=datetime.now(timezone.utc))
        make_quiz_attempt(db_session, user_id, subj.id, percentage=90.0,
                          completed_at=datetime.now(timezone.utc))

        resp = client.get("/api/analytics/topic-mastery",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["mastery"]) >= 1
        mastery = next(m for m in data["mastery"] if m["subject_id"] == subj.id)
        assert mastery["subject_name"] == "Chemistry"
        assert mastery["quizzes_attempted"] == 2
        # average quiz = (70+90)/2 = 80
        # study_completion = min(100, 10/1*100) = 100 (1 lesson total cause only 1 subject? let's see...)
        # The total_lessons comes from subject.lessons which we didn't create any, so it's 0 → max(1, 0) = 1
        # lessons_done = 10, so study_completion = min(100, 10/1 * 100) = 100
        # concept_understanding = min(100, 80*0.7 + 100*0.3) = min(100, 56+30) = 86
        # problem_solving = min(100, 80*0.6 + 100*0.4) = min(100, 48+40) = 88
        # exam_readiness = min(100, 80*0.8 + 100*0.2) = min(100, 64+20) = 84
        # overall_mastery = (86+88+84)/3 = 86.0
        assert mastery["mastery_percentage"] == 86.0


# ---------------------------------------------------------------------------
# 5. Strong / Weak subjects
# ---------------------------------------------------------------------------

class TestStrongWeakSubjects:
    def test_strong_and_weak_calculation(self, client: TestClient, db_session):
        """Strong=top 3 by avg score, Weak=bottom 3 by avg score."""
        info = signup_and_token(client)
        user_id = info["user"]["id"]

        subjs = []
        for name, score in [("A", 90), ("B", 80), ("C", 70), ("D", 60), ("E", 50)]:
            s = make_subject(db_session, name, name.lower(), "science")
            make_progress(db_session, user_id, s.id, average_score=score)
            subjs.append(s)

        resp = client.get("/api/analytics/overview",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()

        strong_names = [s["subject_name"] for s in data["strong_subjects"]]
        weak_names = [s["subject_name"] for s in data["weak_subjects"]]

        # Strong = top 3 → A(90), B(80), C(70)
        assert "A" in strong_names
        assert "B" in strong_names
        assert "C" in strong_names
        assert "D" not in strong_names

        # Weak = bottom 3 → E(50), D(60), C(70) — but C is also strong
        assert "E" in weak_names
        assert "D" in weak_names


# ---------------------------------------------------------------------------
# 6. Overall average
# ---------------------------------------------------------------------------

class TestOverallAverage:
    def test_average_of_mixed_scores(self, client: TestClient, db_session, monkeypatch):
        """Overall average includes both quiz and exam scores."""
        monkeypatch.setattr(QuestionPoolService, "get_questions_for_quiz",
                            lambda *a, **kw: [])
        info = signup_and_token(client)
        user_id = info["user"]["id"]
        subj = make_subject(db_session)

        make_quiz_attempt(db_session, user_id, subj.id, percentage=100.0)
        make_quiz_attempt(db_session, user_id, subj.id, percentage=50.0)

        exam = Exam(id=str(uuid.uuid4()), subject_id=subj.id, title="E",
                    exam_type="JAMB")
        db_session.add(exam)
        db_session.commit()
        make_exam_result(db_session, user_id, exam, percentage=75.0)

        resp = client.get("/api/analytics/overview",
                          headers={"Authorization": f"Bearer {info['token']}"})
        data = resp.json()
        # (100 + 50 + 75) / 3 = 75.0
        assert data["overall_average"] == 75.0

    def test_no_scores_returns_zero(self, client: TestClient, db_session):
        info = signup_and_token(client)
        resp = client.get("/api/analytics/overview",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.json()["overall_average"] == 0.0


# ---------------------------------------------------------------------------
# 7. Improvement rate
# ---------------------------------------------------------------------------

class TestImprovementRate:
    def test_no_data(self, client: TestClient, db_session):
        info = signup_and_token(client)
        resp = client.get("/api/analytics/overview",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.json()["improvement_rate"] == 0.0

    def test_single_attempt(self, client: TestClient, db_session):
        """Single attempt → improvement_rate = 0.0."""
        info = signup_and_token(client)
        user_id = info["user"]["id"]
        subj = make_subject(db_session)
        make_quiz_attempt(db_session, user_id, subj.id, percentage=70.0)

        resp = client.get("/api/analytics/overview",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.json()["improvement_rate"] == 0.0

    def test_multiple_attempts_improving(self, client: TestClient, db_session):
        """Improvement rate reflects slope: (last - first) / count."""
        info = signup_and_token(client)
        user_id = info["user"]["id"]
        subj = make_subject(db_session)

        now = datetime.now(timezone.utc)
        make_quiz_attempt(db_session, user_id, subj.id, percentage=40.0,
                          completed_at=now - timedelta(days=10))
        make_quiz_attempt(db_session, user_id, subj.id, percentage=60.0,
                          completed_at=now - timedelta(days=5))
        make_quiz_attempt(db_session, user_id, subj.id, percentage=80.0,
                          completed_at=now - timedelta(days=1))

        resp = client.get("/api/analytics/overview",
                          headers={"Authorization": f"Bearer {info['token']}"})
        data = resp.json()
        # change = last(80) - first(40) = 40, count = 3
        # rate = 40 / 3 = 13.33
        assert data["improvement_rate"] == pytest.approx(13.33, abs=0.01)

    def test_multiple_attempts_declining(self, client: TestClient, db_session):
        """Negative improvement when scores decline."""
        info = signup_and_token(client)
        user_id = info["user"]["id"]
        subj = make_subject(db_session)

        now = datetime.now(timezone.utc)
        make_quiz_attempt(db_session, user_id, subj.id, percentage=90.0,
                          completed_at=now - timedelta(days=10))
        make_quiz_attempt(db_session, user_id, subj.id, percentage=50.0,
                          completed_at=now - timedelta(days=5))

        resp = client.get("/api/analytics/overview",
                          headers={"Authorization": f"Bearer {info['token']}"})
        data = resp.json()
        # change = 50 - 90 = -40, count = 2
        # rate = -40 / 2 = -20.0
        assert data["improvement_rate"] == -20.0


# ---------------------------------------------------------------------------
# 8. Error handling
# ---------------------------------------------------------------------------

class TestAnalyticsErrorHandling:
    def test_dashboard_no_auth(self, client: TestClient):
        resp = client.get("/api/analytics/dashboard")
        assert resp.status_code in (401, 403)

    def test_overview_no_auth(self, client: TestClient):
        resp = client.get("/api/analytics/overview")
        assert resp.status_code in (401, 403)

    def test_invalid_token(self, client: TestClient):
        headers = {"Authorization": "Bearer invalidtoken"}
        for path in ("/api/analytics/dashboard", "/api/analytics/overview",
                     "/api/analytics/accuracy-trends", "/api/analytics/topic-mastery"):
            resp = client.get(path, headers=headers)
            assert resp.status_code in (401, 403), f"{path} returned {resp.status_code}"
