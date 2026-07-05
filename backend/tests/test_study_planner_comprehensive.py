import pytest
import json
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.models.study_plan import StudyPlan, StudyPlanDay
from app.models.subject import Subject
from app.models.lesson import Lesson, Topic
from app.models.quiz import Quiz, Question, QuizAttempt, QuizAnswer
from app.database.base import Base, get_db
from app.main import app


def _signup(client: TestClient, email: str) -> dict:
    resp = client.post("/api/auth/signup", json={
        "email": email,
        "password": "TestPassword123!",
        "full_name": "Test User",
    })
    assert resp.status_code == 201
    return resp.json()


def _token(resp: dict) -> str:
    return resp["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_subject(db, name: str = "Mathematics") -> Subject:
    subj = Subject(name=name, slug=name.lower(), category="Science")
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return subj


def _create_lesson(db, subject_id: str, title: str = "Algebra") -> Lesson:
    lesson = Lesson(subject_id=subject_id, title=title, slug=title.lower(), content="Algebra content")
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    return lesson


def _create_topic(db, lesson_id: str, title: str = "Linear Equations") -> Topic:
    topic = Topic(lesson_id=lesson_id, title=title, content=f"Content about {title}")
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


# ---------- get_plans ----------

def test_get_plans_empty(client: TestClient):
    resp = _signup(client, "plans_empty@test.com")
    token = _token(resp)

    response = client.get("/api/study-planner", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["plans"] == []
    assert data["total"] == 0


def test_get_plans_with_plans(client: TestClient):
    resp = _signup(client, "plans_with@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=10)).isoformat()
    client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Plan A", "plan_type": "exam", "start_date": today,
        "end_date": future, "subjects": ["Mathematics"],
    })
    client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Plan B", "plan_type": "daily", "start_date": today,
        "end_date": future, "subjects": ["Mathematics"],
    })

    response = client.get("/api/study-planner", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    titles = {p["title"] for p in data["plans"]}
    assert titles == {"Plan A", "Plan B"}


def test_get_plans_with_days(client: TestClient):
    resp = _signup(client, "plans_days@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=3)).isoformat()
    create_resp = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Plan With Days", "plan_type": "exam",
        "start_date": today, "end_date": future, "subjects": ["Mathematics"],
    })
    assert create_resp.status_code == 200

    response = client.get("/api/study-planner", headers=_auth_header(token))
    assert response.status_code == 200
    plan = response.json()["plans"][0]
    assert len(plan["days"]) > 0
    assert "id" in plan["days"][0]
    assert "date" in plan["days"][0]
    assert "subjects" in plan["days"][0]
    assert "is_completed" in plan["days"][0]


# ---------- get_plan ----------

def test_get_plan_existing(client: TestClient):
    resp = _signup(client, "get_plan_ok@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=5)).isoformat()
    create_resp = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "My Plan", "plan_type": "daily",
        "start_date": today, "end_date": future, "subjects": ["Mathematics"],
    })
    plan_id = create_resp.json()["id"]

    response = client.get(f"/api/study-planner/{plan_id}", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "My Plan"
    assert data["id"] == plan_id
    assert len(data["days"]) > 0


def test_get_plan_not_found(client: TestClient):
    resp = _signup(client, "get_plan_nf@test.com")
    token = _token(resp)

    response = client.get("/api/study-planner/nonexistent-id-123", headers=_auth_header(token))
    assert response.status_code == 404


def test_get_plan_wrong_user(client: TestClient):
    resp1 = _signup(client, "plan_owner@test.com")
    token1 = _token(resp1)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=5)).isoformat()
    create_resp = client.post("/api/study-planner", headers=_auth_header(token1), json={
        "title": "My Plan", "plan_type": "daily",
        "start_date": today, "end_date": future, "subjects": ["Mathematics"],
    })
    plan_id = create_resp.json()["id"]

    resp2 = _signup(client, "plan_intruder@test.com")
    token2 = _token(resp2)

    response = client.get(f"/api/study-planner/{plan_id}", headers=_auth_header(token2))
    assert response.status_code == 404


# ---------- create_plan ----------

def test_create_plan_mandatory_fields(client: TestClient):
    resp = _signup(client, "create_mandatory@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Mandatory Only",
        "plan_type": "exam",
        "start_date": today,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Mandatory Only"
    assert "id" in data
    assert data["start_date"] == today


def test_create_plan_with_end_date(client: TestClient):
    resp = _signup(client, "create_enddate@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=14)).isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "With End Date",
        "plan_type": "exam",
        "start_date": today,
        "end_date": future,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["end_date"] == future
    assert len(data["days"]) > 0


def test_create_plan_without_end_date_defaults_30_days(client: TestClient):
    resp = _signup(client, "create_noend@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "No End Date",
        "plan_type": "daily",
        "start_date": today,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["end_date"] is not None
    expected_end = (date.today() + timedelta(days=30)).isoformat()
    assert data["end_date"] == expected_end


def test_create_plan_empty_subjects_returns_error(client: TestClient):
    resp = _signup(client, "create_emptysubj@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    with pytest.raises(Exception):
        client.post("/api/study-planner", headers=_auth_header(token), json={
            "title": "Empty Subjects",
            "plan_type": "exam",
            "start_date": today,
            "subjects": [],
        })


def test_create_plan_sql_injection_title(client: TestClient):
    resp = _signup(client, "create_sqli@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "'; DROP TABLE study_plans; --",
        "plan_type": "exam",
        "start_date": today,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "'; DROP TABLE study_plans; --"


def test_create_plan_special_characters(client: TestClient):
    resp = _signup(client, "create_special@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Plan with emoji 🔥 and résumé",
        "plan_type": "exam",
        "start_date": today,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Plan with emoji 🔥 and résumé"


def test_create_plan_very_long_title(client: TestClient):
    resp = _signup(client, "create_long@test.com")
    token = _token(resp)

    long_title = "A" * 500
    today = date.today().isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": long_title,
        "plan_type": "exam",
        "start_date": today,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    assert response.json()["title"] == long_title


# ---------- mark_day_completed ----------

def test_mark_day_completed_valid(client: TestClient):
    resp = _signup(client, "markday_ok@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=3)).isoformat()
    plan_resp = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Mark Day", "plan_type": "exam",
        "start_date": today, "end_date": future, "subjects": ["Mathematics"],
    })
    day_id = plan_resp.json()["days"][0]["id"]

    response = client.post(f"/api/study-planner/days/{day_id}/complete", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == day_id
    assert data["is_completed"] == "true"


def test_mark_day_completed_already_completed(client: TestClient):
    resp = _signup(client, "markday_already@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=3)).isoformat()
    plan_resp = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Already Done", "plan_type": "exam",
        "start_date": today, "end_date": future, "subjects": ["Mathematics"],
    })
    day_id = plan_resp.json()["days"][0]["id"]

    client.post(f"/api/study-planner/days/{day_id}/complete", headers=_auth_header(token))
    response = client.post(f"/api/study-planner/days/{day_id}/complete", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["is_completed"] == "true"


def test_mark_day_completed_not_found(client: TestClient):
    resp = _signup(client, "markday_nf@test.com")
    token = _token(resp)

    response = client.post("/api/study-planner/days/nonexistent-day-id/complete", headers=_auth_header(token))
    assert response.status_code == 404


def test_mark_day_completed_wrong_user(client: TestClient):
    resp1 = _signup(client, "markday_owner@test.com")
    token1 = _token(resp1)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=3)).isoformat()
    plan_resp = client.post("/api/study-planner", headers=_auth_header(token1), json={
        "title": "Owner Plan", "plan_type": "exam",
        "start_date": today, "end_date": future, "subjects": ["Mathematics"],
    })
    day_id = plan_resp.json()["days"][0]["id"]

    resp2 = _signup(client, "markday_intruder@test.com")
    token2 = _token(resp2)

    response = client.post(f"/api/study-planner/days/{day_id}/complete", headers=_auth_header(token2))
    assert response.status_code == 404


# ---------- get_today_tasks ----------

def test_get_today_tasks_no_tasks(client: TestClient):
    resp = _signup(client, "today_none@test.com")
    token = _token(resp)

    response = client.get("/api/study-planner/today", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["tasks"] == []
    assert data["total"] == 0


def test_get_today_tasks_with_tasks(client: TestClient):
    resp = _signup(client, "today_with@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=3)).isoformat()
    client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Today Plan", "plan_type": "exam",
        "start_date": today, "end_date": future, "subjects": ["Mathematics"],
    })

    response = client.get("/api/study-planner/today", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] > 0
    assert data["date"] == today
    for task in data["tasks"]:
        assert "id" in task
        assert "plan_id" in task
        assert "subjects" in task


def test_get_today_tasks_with_completed_and_incomplete(client: TestClient):
    resp = _signup(client, "today_mixed@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=3)).isoformat()
    plan_resp = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Mixed Plan", "plan_type": "exam",
        "start_date": today, "end_date": future, "subjects": ["Mathematics"],
    })
    days = plan_resp.json()["days"]

    client.post(f"/api/study-planner/days/{days[0]['id']}/complete", headers=_auth_header(token))

    response = client.get("/api/study-planner/today", headers=_auth_header(token))
    assert response.status_code == 200
    tasks = response.json()["tasks"]
    completed = [t for t in tasks if t["is_completed"] == "true"]
    incomplete = [t for t in tasks if t["is_completed"] == "false"]
    assert len(completed) >= 1
    assert len(incomplete) >= 0


# ---------- get_weekly_calendar ----------

def test_get_weekly_calendar_with_week_start(client: TestClient):
    resp = _signup(client, "cal_with@test.com")
    token = _token(resp)

    today = date.today()
    future = today + timedelta(days=10)
    client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Calendar Plan", "plan_type": "exam",
        "start_date": today.isoformat(), "end_date": future.isoformat(),
        "subjects": ["Mathematics"],
    })

    week_start = today.isoformat()
    response = client.get(f"/api/study-planner/calendar?week_start={week_start}", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["start_date"] == week_start
    assert "end_date" in data
    assert "calendar" in data


def test_get_weekly_calendar_without_week_start(client: TestClient):
    resp = _signup(client, "cal_without@test.com")
    token = _token(resp)

    today = date.today()
    future = today + timedelta(days=10)
    client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Calendar Plan 2", "plan_type": "exam",
        "start_date": today.isoformat(), "end_date": future.isoformat(),
        "subjects": ["Mathematics"],
    })

    response = client.get("/api/study-planner/calendar", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    monday = today - timedelta(days=today.weekday())
    assert data["start_date"] == monday.isoformat()


def test_get_weekly_calendar_no_data(client: TestClient):
    resp = _signup(client, "cal_nodata@test.com")
    token = _token(resp)

    response = client.get("/api/study-planner/calendar", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["calendar"] == {}


# ---------- check_and_suggest_reviews ----------
# This endpoint is called internally — we test via service directly

def _get_test_db(client):
    """Get the testing DB session from the app's dependency override."""
    from app.database.base import get_db
    override = app.dependency_overrides.get(get_db)
    if override:
        gen = override()
        return next(gen)
    return None


def test_check_and_suggest_reviews_high_score_no_suggestion(client: TestClient):
    from app.services.study_plan_service import StudyPlanService

    resp = _signup(client, "review_high@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    assert db is not None, "Could not get test DB session"

    subject = _create_subject(db, "English")
    quiz = Quiz(subject_id=subject.id, title="English Quiz", difficulty="medium")
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    attempt = QuizAttempt(quiz_id=quiz.id, user_id=uid, score="8", total="10")
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    service = StudyPlanService(db)
    result = service.check_and_suggest_reviews(uid, attempt.id)
    assert result is None


def test_check_and_suggest_reviews_low_score_creates_review(client: TestClient):
    from app.services.study_plan_service import StudyPlanService

    resp = _signup(client, "review_low@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    assert db is not None

    subject = _create_subject(db, "English")
    quiz = Quiz(subject_id=subject.id, title="Tough Quiz", difficulty="hard")
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    attempt = QuizAttempt(quiz_id=quiz.id, user_id=uid, score="3", total="10")
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    wrong_answer = QuizAnswer(attempt_id=attempt.id, selected_answer="A", is_correct=False)
    db.add(wrong_answer)
    db.commit()

    service = StudyPlanService(db)
    result = service.check_and_suggest_reviews(uid, attempt.id)
    assert result is not None
    assert "plan_id" in result
    assert "review session" in result["reason"].lower()
    assert result["days"] > 0


def test_check_and_suggest_reviews_no_attempt(client: TestClient):
    from app.services.study_plan_service import StudyPlanService

    resp = _signup(client, "review_noattempt@test.com")
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    assert db is not None

    service = StudyPlanService(db)
    result = service.check_and_suggest_reviews(uid, "nonexistent-attempt-id")
    assert result is None


# ---------- Scheduling algorithm edge cases ----------

def test_scheduling_one_day_plan(client: TestClient):
    resp = _signup(client, "sched_1day@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "One Day Plan", "plan_type": "exam",
        "start_date": today, "end_date": today,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["days"]) >= 1


def test_scheduling_long_plan(client: TestClient):
    resp = _signup(client, "sched_long@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    end = (date.today() + timedelta(days=89)).isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "90 Day Plan", "plan_type": "exam",
        "start_date": today, "end_date": end,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["days"]) > 0
    assert data["end_date"] == end


def test_scheduling_single_subject(client: TestClient):
    resp = _signup(client, "sched_1subj@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=7)).isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Single Subject", "plan_type": "daily",
        "start_date": today, "end_date": future,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    for day in response.json()["days"]:
        assert "Mathematics" in day["subjects"]


def test_scheduling_multiple_subjects(client: TestClient):
    resp = _signup(client, "sched_multi@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=14)).isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Multi Subject", "plan_type": "exam",
        "start_date": today, "end_date": future,
        "subjects": ["Mathematics", "English"],
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["days"]) > 0
    all_subjects = set()
    for day in data["days"]:
        all_subjects.update(day["subjects"])
    assert len(all_subjects) > 0


# ---------- Input validation ----------

def test_create_plan_invalid_dates(client: TestClient):
    resp = _signup(client, "invalid_dates@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "Past End", "plan_type": "exam",
        "start_date": today, "end_date": yesterday,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200


def test_get_plans_unauthorized(client: TestClient):
    response = client.get("/api/study-planner")
    assert response.status_code == 401 or response.status_code == 403


def test_create_plan_with_null_values(client: TestClient):
    resp = _signup(client, "null_values@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=3)).isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": None,
        "plan_type": None,
        "start_date": None,
        "subjects": None,
    })
    assert response.status_code == 422


def test_create_plan_empty_string_title_accepted(client: TestClient):
    resp = _signup(client, "empty_title@test.com")
    token = _token(resp)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=5)).isoformat()
    response = client.post("/api/study-planner", headers=_auth_header(token), json={
        "title": "",
        "plan_type": "",
        "start_date": today,
        "end_date": future,
        "subjects": ["Mathematics"],
    })
    assert response.status_code == 200
    data = response.json()
    assert len(data["days"]) > 0


# ---------- Auth isolation ----------

def test_plans_isolation_between_users(client: TestClient):
    resp1 = _signup(client, "iso_user1@test.com")
    token1 = _token(resp1)

    resp2 = _signup(client, "iso_user2@test.com")
    token2 = _token(resp2)

    today = date.today().isoformat()
    future = (date.today() + timedelta(days=5)).isoformat()
    client.post("/api/study-planner", headers=_auth_header(token1), json={
        "title": "User1 Plan", "plan_type": "exam",
        "start_date": today, "end_date": future, "subjects": ["Mathematics"],
    })

    resp2_plans = client.get("/api/study-planner", headers=_auth_header(token2))
    assert resp2_plans.json()["total"] == 0


# ---------- Service-level: scheduling algorithm ----------

def test_scheduling_algorithm_single_day():
    from app.services.study_plan_service import StudyPlanService

    subjects = ["Math"]
    start = date.today()
    end = start

    service = StudyPlanService.__new__(StudyPlanService)
    tasks = service._scheduling_algorithm(subjects, start, end)
    assert len(tasks) >= 1
    for t in tasks:
        assert start <= t["date"] <= end


def test_scheduling_algorithm_many_subjects():
    from app.services.study_plan_service import StudyPlanService

    subjects = ["Math", "English", "Physics", "Chemistry", "Biology"]
    start = date.today()
    end = start + timedelta(days=30)

    service = StudyPlanService.__new__(StudyPlanService)
    tasks = service._scheduling_algorithm(subjects, start, end)
    assert len(tasks) > 0
    all_dates = [t["date"] for t in tasks]
    assert min(all_dates) >= start
    assert max(all_dates) <= end


def test_scheduling_algorithm_review_intervals():
    from app.services.study_plan_service import StudyPlanService

    subjects = ["Math"]
    start = date.today()
    end = start + timedelta(days=14)

    service = StudyPlanService.__new__(StudyPlanService)
    tasks = service._scheduling_algorithm(subjects, start, end)

    review_tasks = [t for t in tasks if any("Review:" in topic for topic in t["topics"])]
    assert len(review_tasks) > 0
