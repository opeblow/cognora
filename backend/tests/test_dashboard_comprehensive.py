import pytest
from datetime import timedelta, datetime, timezone
from fastapi.testclient import TestClient
from uuid import uuid4

from app.core.config import settings
from app.database.base import get_db
from app.models.user import User
from app.models.subject import Subject
from app.models.progress import UserProgress as UserProgressModel

from app.main import app


# ---------------------------------------------------------------------------
# Autouse fixtures (mock_redis is already autouse in conftest.py)
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    monkeypatch.setattr("app.utils.email.EmailService.__init__", lambda self: None)
    monkeypatch.setattr("app.utils.email.EmailService.send_verification_email", lambda self, to, token: True)
    monkeypatch.setattr("app.utils.email.EmailService.send_password_reset_email", lambda self, to, token: True)


@pytest.fixture
def user_token(client, db_session):
    resp = client.post("/api/auth/signup", json={
        "email": "dash@test.com", "password": "ValidPass123!", "full_name": "Dashboard User",
    })
    assert resp.status_code == 201
    data = resp.json()
    return data["access_token"], data["refresh_token"], data["user"]["id"]


@pytest.fixture
def auth_headers(user_token):
    token, _, _ = user_token
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def single_name_token(client):
    resp = client.post("/api/auth/signup", json={
        "email": "single@test.com", "password": "ValidPass123!", "full_name": "Mono",
    })
    return resp.json()["access_token"]


@pytest.fixture
def empty_name_token(client, db_session):
    resp = client.post("/api/auth/signup", json={
        "email": "empty@test.com", "password": "ValidPass123!", "full_name": "Temp",
    })
    token = resp.json()["access_token"]
    user = db_session.query(User).filter(User.email == "empty@test.com").first()
    user.full_name = ""
    db_session.commit()
    return token


@pytest.fixture
def subjects(db_session):
    subjects_data = [
        Subject(id=str(uuid4()), name="Mathematics", slug="mathematics", category="stem", order_index=1),
        Subject(id=str(uuid4()), name="English Language", slug="english-language", category="language", order_index=2),
        Subject(id=str(uuid4()), name="Physics", slug="physics", category="stem", order_index=3),
        Subject(id=str(uuid4()), name="Chemistry", slug="chemistry", category="stem", order_index=4),
        Subject(id=str(uuid4()), name="Biology", slug="biology", category="stem", order_index=5),
    ]
    for s in subjects_data:
        db_session.add(s)
    db_session.commit()
    for s in subjects_data:
        db_session.refresh(s)
    return subjects_data


_DASH_BASE = "/api/dashboard"


# ---------------------------------------------------------------------------
# Dashboard Basics
# ---------------------------------------------------------------------------

class TestDashboardBasics:
    def test_dashboard_success(self, client: TestClient, auth_headers):
        resp = client.get(_DASH_BASE, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "welcome_name" in data
        assert "credits" in data
        assert "weekly_credits_remaining" in data
        assert "learning_streak" in data
        assert "recent_activity" in data
        assert "progress_overview" in data
        assert "subject_stats" in data
        assert "strong_subjects" in data
        assert "weak_subjects" in data

    def test_welcome_name_full(self, client: TestClient, auth_headers):
        assert client.get(_DASH_BASE, headers=auth_headers).json()["welcome_name"] == "Dashboard"

    def test_welcome_name_single(self, client: TestClient, single_name_token):
        resp = client.get(_DASH_BASE, headers={"Authorization": f"Bearer {single_name_token}"})
        assert resp.json()["welcome_name"] == "Mono"

    def test_welcome_name_empty(self, client: TestClient, empty_name_token):
        resp = client.get(_DASH_BASE, headers={"Authorization": f"Bearer {empty_name_token}"})
        assert resp.json()["welcome_name"] == "Student"

    def test_dashboard_credits_display(self, client: TestClient, auth_headers):
        data = client.get(_DASH_BASE, headers=auth_headers).json()
        assert data["credits"] == 50
        assert data["weekly_credits_remaining"] == settings.FREE_WEEKLY_CREDITS

    def test_dashboard_learning_streak(self, client: TestClient, auth_headers):
        assert client.get(_DASH_BASE, headers=auth_headers).json()["learning_streak"] == 0

    def test_dashboard_requires_auth(self, client: TestClient):
        assert client.get(_DASH_BASE).status_code == 401

    def test_dashboard_nonexistent_user(self, client: TestClient):
        from app.core.security import create_access_token
        fake_token = create_access_token({"sub": "nonexistent", "email": "x"})
        resp = client.get(_DASH_BASE, headers={"Authorization": f"Bearer {fake_token}"})
        assert resp.status_code == 401

    def test_dashboard_credits_after_purchase(self, client: TestClient, auth_headers):
        client.post("/api/credits/purchase", json={"amount": 100}, headers=auth_headers)
        assert client.get(_DASH_BASE, headers=auth_headers).json()["credits"] >= 150


# ---------------------------------------------------------------------------
# Initial State (no activity data)
# ---------------------------------------------------------------------------

class TestInitialState:
    def test_no_progress_empty_lists(self, client: TestClient, auth_headers):
        data = client.get(_DASH_BASE, headers=auth_headers).json()
        assert data["progress_overview"] == []
        assert data["subject_stats"] == []
        assert data["strong_subjects"] == []
        assert data["weak_subjects"] == []
        assert data["recent_activity"] == []

    def test_no_progress_streak_zero(self, client: TestClient, auth_headers):
        assert client.get(_DASH_BASE, headers=auth_headers).json()["learning_streak"] == 0


# ---------------------------------------------------------------------------
# Progress Overview
# ---------------------------------------------------------------------------

class TestProgressOverview:
    def test_single_subject(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        math = subjects[0]
        db_session.add(UserProgressModel(
            id=str(uuid4()), user_id=user_id, subject_id=math.id,
            lessons_completed="5", quizzes_taken="3", average_score="75",
            total_study_time_minutes="120",
        ))
        db_session.commit()

        data = client.get(_DASH_BASE, headers=auth_headers).json()
        assert len(data["progress_overview"]) == 1
        entry = data["progress_overview"][0]
        assert entry["subject_name"] == "Mathematics"
        assert entry["lessons_completed"] == 5
        assert entry["quizzes_taken"] == 3
        assert entry["average_score"] == 75.0
        assert entry["total_study_time_minutes"] == 120

    def test_multiple_subjects(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        math, english, physics = subjects[:3]
        for subj, avg, lessons in [(math, "85", "10"), (english, "70", "8"), (physics, "60", "5")]:
            db_session.add(UserProgressModel(
                id=str(uuid4()), user_id=user_id, subject_id=subj.id,
                lessons_completed=lessons, quizzes_taken="5", average_score=avg,
                total_study_time_minutes="200",
            ))
        db_session.commit()

        names = {e["subject_name"] for e in client.get(_DASH_BASE, headers=auth_headers).json()["progress_overview"]}
        assert names == {"Mathematics", "English Language", "Physics"}

    def test_progress_structure(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        math = subjects[0]
        db_session.add(UserProgressModel(
            id=str(uuid4()), user_id=user_id, subject_id=math.id,
            lessons_completed="3", quizzes_taken="2", average_score="80",
            total_study_time_minutes="90",
        ))
        db_session.commit()

        entry = client.get(_DASH_BASE, headers=auth_headers).json()["progress_overview"][0]
        assert "subject_id" in entry
        assert "subject_name" in entry
        assert "lessons_completed" in entry
        assert "quizzes_taken" in entry
        assert "average_score" in entry
        assert "total_study_time_minutes" in entry

    def test_progress_missing_subject(self, client: TestClient, db_session, auth_headers, user_token):
        _, _, user_id = user_token
        db_session.add(UserProgressModel(
            id=str(uuid4()), user_id=user_id, subject_id="nonexistent-subject-id",
            lessons_completed="5", quizzes_taken="3", average_score="80",
            total_study_time_minutes="60",
        ))
        db_session.commit()
        assert client.get(_DASH_BASE, headers=auth_headers).json()["progress_overview"] == []

    def test_progress_zero_values(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        math = subjects[0]
        db_session.add(UserProgressModel(
            id=str(uuid4()), user_id=user_id, subject_id=math.id,
            lessons_completed="0", quizzes_taken="0", average_score="0",
            total_study_time_minutes="0",
        ))
        db_session.commit()

        entry = client.get(_DASH_BASE, headers=auth_headers).json()["progress_overview"][0]
        assert entry["lessons_completed"] == 0
        assert entry["quizzes_taken"] == 0
        assert entry["average_score"] == 0.0
        assert entry["total_study_time_minutes"] == 0


# ---------------------------------------------------------------------------
# Strong / Weak Subjects
# ---------------------------------------------------------------------------

class TestStrongWeakSubjects:
    def test_strong_subjects_ordered(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        math, english, physics, chemistry, biology = subjects
        for subj, avg in [(math, "50"), (english, "90"), (physics, "40"), (chemistry, "80"), (biology, "70")]:
            db_session.add(UserProgressModel(
                id=str(uuid4()), user_id=user_id, subject_id=subj.id,
                lessons_completed="5", quizzes_taken="3", average_score=avg,
                total_study_time_minutes="100",
            ))
        db_session.commit()

        strong = client.get(_DASH_BASE, headers=auth_headers).json()["strong_subjects"]
        assert len(strong) == 3
        assert [s["subject_name"] for s in strong] == ["English Language", "Chemistry", "Biology"]

    def test_weak_subjects_ordered(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        math, english, physics, chemistry, biology = subjects
        for subj, avg in [(math, "50"), (english, "90"), (physics, "40"), (chemistry, "80"), (biology, "70")]:
            db_session.add(UserProgressModel(
                id=str(uuid4()), user_id=user_id, subject_id=subj.id,
                lessons_completed="5", quizzes_taken="3", average_score=avg,
                total_study_time_minutes="100",
            ))
        db_session.commit()

        weak = client.get(_DASH_BASE, headers=auth_headers).json()["weak_subjects"]
        assert len(weak) == 3
        assert [s["subject_name"] for s in weak] == ["Physics", "Mathematics", "Biology"]

    def test_less_than_three_subjects(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        math = subjects[0]
        db_session.add(UserProgressModel(
            id=str(uuid4()), user_id=user_id, subject_id=math.id,
            lessons_completed="5", quizzes_taken="3", average_score="75",
            total_study_time_minutes="100",
        ))
        db_session.commit()

        data = client.get(_DASH_BASE, headers=auth_headers).json()
        assert len(data["strong_subjects"]) == 1
        assert len(data["weak_subjects"]) == 1
        assert data["strong_subjects"][0]["subject_name"] == "Mathematics"
        assert data["weak_subjects"][0]["subject_name"] == "Mathematics"


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_no_progress(self, client: TestClient, auth_headers):
        data = client.get(_DASH_BASE, headers=auth_headers).json()
        assert data["progress_overview"] == []

    def test_all_perfect_scores(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        for subj in subjects[:3]:
            db_session.add(UserProgressModel(
                id=str(uuid4()), user_id=user_id, subject_id=subj.id,
                lessons_completed="10", quizzes_taken="10", average_score="100",
                total_study_time_minutes="500",
            ))
        db_session.commit()

        data = client.get(_DASH_BASE, headers=auth_headers).json()
        assert all(e["average_score"] == 100.0 for e in data["progress_overview"])
        assert all(s["average_score"] == 100.0 for s in data["strong_subjects"])
        assert all(s["average_score"] == 100.0 for s in data["weak_subjects"])

    def test_all_zero_scores(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        for subj in subjects[:3]:
            db_session.add(UserProgressModel(
                id=str(uuid4()), user_id=user_id, subject_id=subj.id,
                lessons_completed="0", quizzes_taken="0", average_score="0",
                total_study_time_minutes="0",
            ))
        db_session.commit()

        data = client.get(_DASH_BASE, headers=auth_headers).json()
        assert all(e["average_score"] == 0.0 for e in data["progress_overview"])
        assert all(s["average_score"] == 0.0 for s in data["strong_subjects"])

    def test_very_high_values(self, client: TestClient, db_session, auth_headers, user_token, subjects):
        _, _, user_id = user_token
        math = subjects[0]
        db_session.add(UserProgressModel(
            id=str(uuid4()), user_id=user_id, subject_id=math.id,
            lessons_completed="999", quizzes_taken="999", average_score="99.9",
            total_study_time_minutes="99999",
        ))
        db_session.commit()

        entry = client.get(_DASH_BASE, headers=auth_headers).json()["progress_overview"][0]
        assert entry["average_score"] == 99.9
        assert entry["lessons_completed"] == 999
        assert entry["quizzes_taken"] == 999
        assert entry["total_study_time_minutes"] == 99999

    def test_welcome_name_multiple_spaces(self, client: TestClient):
        resp = client.post("/api/auth/signup", json={
            "email": "multiname@test.com", "password": "ValidPass123!",
            "full_name": "John  Michael   Doe",
        })
        data = client.get(_DASH_BASE, headers={"Authorization": f"Bearer {resp.json()['access_token']}"}).json()
        assert data["welcome_name"] == "John"

    def test_welcome_name_special_chars(self, client: TestClient):
        resp = client.post("/api/auth/signup", json={
            "email": "specialname@test.com", "password": "ValidPass123!",
            "full_name": "Dr. O'Brien-Smith",
        })
        data = client.get(_DASH_BASE, headers={"Authorization": f"Bearer {resp.json()['access_token']}"}).json()
        assert data["welcome_name"] == "Dr."

    def test_weekly_credits_remaining_after_deductions(self, client: TestClient, db_session, auth_headers, user_token):
        _, _, user_id = user_token
        from app.services.credit_service import CreditService
        from app.database.base import get_db as original_get_db
        gen = app.dependency_overrides[original_get_db]()
        s = next(gen)
        CreditService(s).deduct_credits(user_id, "ai_ask")
        CreditService(s).deduct_credits(user_id, "generate_quiz")
        s.close()

        data = client.get(_DASH_BASE, headers=auth_headers).json()
        assert data["weekly_credits_remaining"] == settings.FREE_WEEKLY_CREDITS - 3
