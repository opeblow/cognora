import pytest
import uuid
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.models.subject import Subject
from app.models.exam import Exam, ExamQuestion, ExamResult, ExamAnswer
from app.services.exam_service import ExamService
from app.services.credit_service import CreditService


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


def make_exam(db, subject_id, title="Test Exam", exam_type="JAMB", year="2024",
              time_limit_minutes=40, total_questions=5, pass_percentage=40):
    e = Exam(
        id=str(uuid.uuid4()),
        subject_id=subject_id,
        title=title,
        exam_type=exam_type,
        year=year,
        time_limit_minutes=time_limit_minutes,
        total_questions=total_questions,
        pass_percentage=pass_percentage,
        is_active=True,
    )
    db.add(e)
    db.commit()
    return e


def make_exam_question(db, exam_id, text="Exam Q?", correct_answer="A", order_index=1):
    eq = ExamQuestion(
        id=str(uuid.uuid4()),
        exam_id=exam_id,
        text=text,
        options=["A) Option A", "B) Option B", "C) Option C", "D) Option D"],
        correct_answer=correct_answer,
        order_index=order_index,
    )
    db.add(eq)
    db.commit()
    return eq


def make_exam_result(db, exam_id, user_id, status="in_progress"):
    r = ExamResult(
        id=str(uuid.uuid4()),
        exam_id=exam_id,
        user_id=user_id,
        status=status,
    )
    db.add(r)
    db.commit()
    return r


def signup_and_token(client: TestClient, email: str = None) -> dict:
    email = email or f"exam_{uuid.uuid4().hex[:8]}@test.com"
    resp = client.post("/api/auth/signup", json={
        "email": email,
        "password": "TestPassword123!",
        "full_name": "Exam Tester",
    })
    assert resp.status_code == 201
    data = resp.json()
    return {"token": data["access_token"], "user": data["user"], "email": email}


# ---------------------------------------------------------------------------
# 1. get_exams
# ---------------------------------------------------------------------------

class TestGetExams:
    def test_empty(self, client: TestClient, db_session):
        info = signup_and_token(client)
        resp = client.get("/api/exams", headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["exams"] == []
        assert data["total"] == 0

    def test_filter_by_subject(self, client: TestClient, db_session):
        info = signup_and_token(client)
        s1 = make_subject(db_session, "Maths", "maths", "science")
        s2 = make_subject(db_session, "English", "english", "arts")
        e1 = make_exam(db_session, s1.id, "Math Exam")
        e2 = make_exam(db_session, s2.id, "English Exam")

        resp = client.get(f"/api/exams?subject_id={s1.id}",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        ids = [e["id"] for e in data["exams"]]
        assert e1.id in ids
        assert e2.id not in ids
        assert data["total"] == 1

    def test_filter_by_type(self, client: TestClient, db_session):
        info = signup_and_token(client)
        subj = make_subject(db_session)
        jamb_exam = make_exam(db_session, subj.id, "JAMB Test", exam_type="JAMB")
        waec_exam = make_exam(db_session, subj.id, "WAEC Test", exam_type="WAEC")

        resp = client.get(f"/api/exams?exam_type=WAEC",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        ids = [e["id"] for e in data["exams"]]
        assert waec_exam.id in ids
        assert jamb_exam.id not in ids

    def test_pagination(self, client: TestClient, db_session):
        info = signup_and_token(client)
        subj = make_subject(db_session)
        ids = []
        for i in range(5):
            e = make_exam(db_session, subj.id, f"Exam {i}")
            ids.append(e.id)

        resp = client.get("/api/exams?page=1&page_size=2",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["exams"]) == 2
        assert data["total"] == 5

        resp2 = client.get("/api/exams?page=3&page_size=2",
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp2.status_code == 200
        assert len(resp2.json()["exams"]) == 1


# ---------------------------------------------------------------------------
# 2. start_exam
# ---------------------------------------------------------------------------

class TestStartExam:
    def test_new_exam(self, client: TestClient, db_session, monkeypatch):
        """Starting a new exam returns questions and result_id."""
        # Allow free credit deduction
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        # Prevent AI question generation
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session, "Maths", "mathematics", "science")
        exam = make_exam(db_session, subj.id, "New Exam", exam_type="JAMB",
                         total_questions=3)
        for i in range(3):
            make_exam_question(db_session, exam.id, f"Q{i}?", "A", i)

        resp = client.post(f"/api/exams/{exam.id}/start",
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert "result_id" in data
        assert data["is_new"] is True
        assert "exam" in data
        assert len(data["exam"]["questions"]) == 3

    def test_resume_in_progress(self, client: TestClient, db_session, monkeypatch):
        """Starting an exam that has an in-progress result returns that result."""
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session)
        exam = make_exam(db_session, subj.id, "Resume Exam", total_questions=2)
        for i in range(2):
            make_exam_question(db_session, exam.id, f"RQ{i}?", "B", i)

        # First start
        resp1 = client.post(f"/api/exams/{exam.id}/start",
                            headers={"Authorization": f"Bearer {info['token']}"})
        assert resp1.status_code == 200
        result_id = resp1.json()["result_id"]

        # Second start — should resume
        resp2 = client.post(f"/api/exams/{exam.id}/start",
                            headers={"Authorization": f"Bearer {info['token']}"})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert data2["result_id"] == result_id
        assert data2["is_new"] is False

    def test_exam_not_found(self, client: TestClient, db_session):
        info = signup_and_token(client)
        fake_id = str(uuid.uuid4())
        resp = client.post(f"/api/exams/{fake_id}/start",
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 3. submit_exam
# ---------------------------------------------------------------------------

class TestSubmitExam:
    def test_completed_successfully(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session)
        exam = make_exam(db_session, subj.id, "Submit Exam", total_questions=3, pass_percentage=40)
        qs = [make_exam_question(db_session, exam.id, f"SQ{i}?", "A", i) for i in range(3)]

        # Start exam
        start_resp = client.post(f"/api/exams/{exam.id}/start",
                                 headers={"Authorization": f"Bearer {info['token']}"})
        assert start_resp.status_code == 200
        result_id = start_resp.json()["result_id"]

        # Submit all correct
        answers = {q.id: "A" for q in qs}
        resp = client.post(f"/api/exams/results/{result_id}/submit",
                           json={"answers": answers, "time_taken_seconds": 120},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 3
        assert data["total"] == 3
        assert data["percentage"] == 100.0
        assert data["passed"] is True
        assert data["status"] == "completed"

    def test_already_completed(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session)
        exam = make_exam(db_session, subj.id, "Double Submit", total_questions=1)
        q = make_exam_question(db_session, exam.id, "Only Q?", "A")

        start_resp = client.post(f"/api/exams/{exam.id}/start",
                                 headers={"Authorization": f"Bearer {info['token']}"})
        result_id = start_resp.json()["result_id"]

        # First submit
        client.post(f"/api/exams/results/{result_id}/submit",
                    json={"answers": {q.id: "A"}, "time_taken_seconds": 10},
                    headers={"Authorization": f"Bearer {info['token']}"})

        # Second submit → should fail (already completed)
        resp2 = client.post(f"/api/exams/results/{result_id}/submit",
                            json={"answers": {q.id: "A"}, "time_taken_seconds": 5},
                            headers={"Authorization": f"Bearer {info['token']}"})
        assert resp2.status_code == 400

    def test_wrong_user(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        u1 = signup_and_token(client, "owner@exam.com")
        u2 = signup_and_token(client, "intruder@exam.com")

        subj = make_subject(db_session)
        exam = make_exam(db_session, subj.id, "Owner Exam", total_questions=1)
        q = make_exam_question(db_session, exam.id, "Q?", "A")

        # u1 starts exam
        start_resp = client.post(f"/api/exams/{exam.id}/start",
                                 headers={"Authorization": f"Bearer {u1['token']}"})
        result_id = start_resp.json()["result_id"]

        # u2 tries to submit u1's result
        resp = client.post(f"/api/exams/results/{result_id}/submit",
                           json={"answers": {q.id: "A"}, "time_taken_seconds": 10},
                           headers={"Authorization": f"Bearer {u2['token']}"})
        assert resp.status_code == 400  # "Exam result not found"

    def test_result_not_found(self, client: TestClient, db_session):
        info = signup_and_token(client)
        fake_id = str(uuid.uuid4())
        resp = client.post(f"/api/exams/results/{fake_id}/submit",
                           json={"answers": {}, "time_taken_seconds": 10},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# 4. get_my_results
# ---------------------------------------------------------------------------

class TestGetMyResults:
    def test_empty(self, client: TestClient, db_session):
        info = signup_and_token(client)
        resp = client.get("/api/exams/results/mine",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["results"] == []
        assert data["total"] == 0

    def test_after_completion(self, client: TestClient, db_session, monkeypatch):
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session)
        exam = make_exam(db_session, subj.id, "Results Exam", total_questions=2)
        qs = [make_exam_question(db_session, exam.id, f"R{i}?", "A", i) for i in range(2)]

        start_resp = client.post(f"/api/exams/{exam.id}/start",
                                 headers={"Authorization": f"Bearer {info['token']}"})
        result_id = start_resp.json()["result_id"]

        client.post(f"/api/exams/results/{result_id}/submit",
                    json={"answers": {q.id: "A" for q in qs}, "time_taken_seconds": 30},
                    headers={"Authorization": f"Bearer {info['token']}"})

        resp = client.get("/api/exams/results/mine",
                          headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        r = data["results"][0]
        assert r["exam_id"] == exam.id
        assert r["status"] in ("completed", "failed")
        assert r["score"] is not None


# ---------------------------------------------------------------------------
# 5. generate_questions
# ---------------------------------------------------------------------------

class TestGenerateQuestions:
    def test_valid(self, client: TestClient, db_session, monkeypatch):
        """generate_questions returns mock questions."""

        async def mock_generate_live(self, exam_id, user_id, num_questions):
            return [
                {"id": "live_1", "text": f"Gen Q{i}?", "options": ["A) A", "B) B", "C) C", "D) D"],
                 "correct_answer": "A", "explanation": "Exp", "difficulty": "hard",
                 "cognitive_level": "analysis"}
                for i in range(num_questions)
            ]

        monkeypatch.setattr(ExamService, "generate_live_questions", mock_generate_live)

        info = signup_and_token(client)
        subj = make_subject(db_session)
        exam = make_exam(db_session, subj.id, "Gen Exam", total_questions=2)

        resp = client.post(f"/api/exams/{exam.id}/generate-questions?num_questions=3",
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["generated"] == 3
        assert len(data["questions"]) == 3

    def test_exam_not_found(self, client: TestClient, db_session):
        info = signup_and_token(client)
        fake_id = str(uuid.uuid4())
        resp = client.post(f"/api/exams/{fake_id}/generate-questions?num_questions=3",
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 6. Exam standards (JAMB vs WAEC)
# ---------------------------------------------------------------------------

class TestExamStandards:
    def test_jamb_explicit_time(self, client: TestClient, db_session, monkeypatch):
        """JAMB exam with explicit time returns that time."""
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session, "Mathematics", "mathematics", "science")
        exam = make_exam(db_session, subj.id, "JAMB Maths", exam_type="JAMB",
                         time_limit_minutes=40, total_questions=50)
        for i in range(50):
            make_exam_question(db_session, exam.id, f"Q{i}?", "A", i)

        resp = client.post(f"/api/exams/{exam.id}/start",
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["time_limit_minutes"] == 40
        assert len(data["exam"]["questions"]) == 50

    def test_waec_explicit_time(self, client: TestClient, db_session, monkeypatch):
        """WAEC exam with explicit time returns that time."""
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session, "Mathematics", "mathematics", "science")
        exam = make_exam(db_session, subj.id, "WAEC Maths", exam_type="WAEC",
                         time_limit_minutes=150, total_questions=60)
        for i in range(60):
            make_exam_question(db_session, exam.id, f"Q{i}?", "A", i)

        resp = client.post(f"/api/exams/{exam.id}/start",
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["time_limit_minutes"] == 150
        assert len(data["exam"]["questions"]) == 60

    def test_jamb_vs_waec_question_count(self, client: TestClient, db_session, monkeypatch):
        """Verify standards dict lookup works (questions count from standard)."""
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])
        from app.services.exam_service import ExamService as ES
        orig_start = ES.start_exam_async

        captured_target = None
        captured_time = None

        async def tracking_start(self, exam_id, user_id):
            nonlocal captured_target, captured_time
            exam = self.exam_repo.get_with_questions(exam_id)
            standards = __import__("app.utils.exam_standards", fromlist=["EXAM_TYPE_STANDARDS"]).EXAM_TYPE_STANDARDS
            std = standards.get(exam.exam_type, {})
            subject_std = std.get(exam.subject.slug, {"questions": 50, "minutes": 60})
            captured_target = exam.total_questions or subject_std["questions"]
            captured_time = exam.time_limit_minutes or subject_std["minutes"]
            return await orig_start(self, exam_id, user_id)

        monkeypatch.setattr(ES, "start_exam_async", tracking_start)

        info = signup_and_token(client)
        subj = make_subject(db_session, "Mathematics", "mathematics", "science")
        jamb_exam = make_exam(db_session, subj.id, "JAMB Maths", exam_type="JAMB",
                              time_limit_minutes=None, total_questions=None)
        waec_exam = make_exam(db_session, subj.id, "WAEC Maths", exam_type="WAEC",
                              time_limit_minutes=None, total_questions=None)

        # JAMB
        client.post(f"/api/exams/{jamb_exam.id}/start",
                    headers={"Authorization": f"Bearer {info['token']}"})
        assert captured_target == 50
        assert captured_time == 40

        # WAEC
        client.post(f"/api/exams/{waec_exam.id}/start",
                    headers={"Authorization": f"Bearer {info['token']}"})
        assert captured_target == 60
        assert captured_time == 150


# ---------------------------------------------------------------------------
# 7. Credit deduction
# ---------------------------------------------------------------------------

class TestCreditDeduction:
    def test_credits_deducted_on_start(self, client: TestClient, db_session, monkeypatch):
        """Starting a new exam deducts credits from the user."""
        deductions = []

        def tracking_deduct(self, user_id, action):
            deductions.append((user_id, action))
            return True

        monkeypatch.setattr(CreditService, "deduct_credits", tracking_deduct)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session)
        exam = make_exam(db_session, subj.id, "Credit Exam", total_questions=2)
        for i in range(2):
            make_exam_question(db_session, exam.id, f"C{i}?", "A", i)

        client.post(f"/api/exams/{exam.id}/start",
                    headers={"Authorization": f"Bearer {info['token']}"})
        assert len(deductions) == 1
        assert deductions[0][1] == "mock_exam"

    def test_credits_not_deducted_on_resume(self, client: TestClient, db_session, monkeypatch):
        """Resuming an in-progress exam does NOT deduct credits."""
        deductions = []

        def tracking_deduct(self, user_id, action):
            deductions.append((user_id, action))
            return True

        monkeypatch.setattr(CreditService, "deduct_credits", tracking_deduct)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session)
        exam = make_exam(db_session, subj.id, "NoDeduction", total_questions=1)
        make_exam_question(db_session, exam.id, "Only?", "A")

        # Start once
        client.post(f"/api/exams/{exam.id}/start",
                    headers={"Authorization": f"Bearer {info['token']}"})
        deductions.clear()  # reset

        # Resume
        client.post(f"/api/exams/{exam.id}/start",
                    headers={"Authorization": f"Bearer {info['token']}"})
        assert len(deductions) == 0


# ---------------------------------------------------------------------------
# 8. Score calculation edge cases
# ---------------------------------------------------------------------------

class TestScoreEdgeCases:
    def test_pass_by_one_percent(self, client: TestClient, db_session, monkeypatch):
        """Score exactly at pass_percentage → passed."""
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session)
        # 5 questions, pass at 60% → need 3/5 = 60%
        exam = make_exam(db_session, subj.id, "Edge Pass", pass_percentage=60, total_questions=5)
        qs = [make_exam_question(db_session, exam.id, f"P{i}?", "A", i) for i in range(5)]

        start_resp = client.post(f"/api/exams/{exam.id}/start",
                                 headers={"Authorization": f"Bearer {info['token']}"})
        result_id = start_resp.json()["result_id"]

        answers = {qs[0].id: "A", qs[1].id: "A", qs[2].id: "A",
                   qs[3].id: "B", qs[4].id: "B"}
        resp = client.post(f"/api/exams/results/{result_id}/submit",
                           json={"answers": answers, "time_taken_seconds": 60},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["percentage"] == 60.0
        assert data["passed"] is True
        assert data["status"] == "completed"

    def test_fail_by_one_percent(self, client: TestClient, db_session, monkeypatch):
        """Score just below pass_percentage → failed."""
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session)
        # 6 questions, pass at 50% → need 3/6 = 50% → 2/6 = 33.33% < 50%
        exam = make_exam(db_session, subj.id, "Edge Fail", pass_percentage=50, total_questions=6)
        qs = [make_exam_question(db_session, exam.id, f"F{i}?", "A", i) for i in range(6)]

        start_resp = client.post(f"/api/exams/{exam.id}/start",
                                 headers={"Authorization": f"Bearer {info['token']}"})
        result_id = start_resp.json()["result_id"]

        answers = {qs[0].id: "A", qs[1].id: "A", qs[2].id: "B",
                   qs[3].id: "B", qs[4].id: "B", qs[5].id: "B"}
        resp = client.post(f"/api/exams/results/{result_id}/submit",
                           json={"answers": answers, "time_taken_seconds": 60},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["percentage"] == pytest.approx(33.33, abs=0.01)
        assert data["passed"] is False
        assert data["status"] == "failed"

    def test_zero_questions_exam(self, client: TestClient, db_session, monkeypatch):
        """Exam with 0 questions returns score=0 without division by zero."""
        monkeypatch.setattr(CreditService, "deduct_credits", lambda *a, **kw: True)
        monkeypatch.setattr(ExamService, "_fetch_live_questions",
                            lambda *a, **kw: [])

        info = signup_and_token(client)
        subj = make_subject(db_session)
        exam = make_exam(db_session, subj.id, "Zero Q Exam", total_questions=0)
        # no questions

        start_resp = client.post(f"/api/exams/{exam.id}/start",
                                 headers={"Authorization": f"Bearer {info['token']}"})
        assert start_resp.status_code == 200
        result_id = start_resp.json()["result_id"]

        resp = client.post(f"/api/exams/results/{result_id}/submit",
                           json={"answers": {}, "time_taken_seconds": 5},
                           headers={"Authorization": f"Bearer {info['token']}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["score"] == 0
        assert data["total"] == 0
        assert data["percentage"] == 0.0


# ---------------------------------------------------------------------------
# 9. Auth / Security
# ---------------------------------------------------------------------------

class TestExamAuth:
    def test_no_auth_on_list(self, client: TestClient):
        resp = client.get("/api/exams")
        assert resp.status_code in (401, 403)

    def test_no_auth_on_start(self, client: TestClient):
        resp = client.post(f"/api/exams/{uuid.uuid4()}/start")
        assert resp.status_code in (401, 403)

    def test_no_auth_on_submit(self, client: TestClient):
        resp = client.post(f"/api/exams/results/{uuid.uuid4()}/submit",
                           json={"answers": {}, "time_taken_seconds": 10})
        assert resp.status_code in (401, 403)

    def test_invalid_token(self, client: TestClient):
        resp = client.get("/api/exams",
                          headers={"Authorization": "Bearer bogus"})
        assert resp.status_code in (401, 403)
