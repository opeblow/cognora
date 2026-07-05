import pytest
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.models.flashcard import Flashcard, FlashcardReview
from app.models.lesson import Lesson, Topic
from app.models.subject import Subject
from app.database.base import Base, get_db
from app.core.config import settings
from app.main import app


def _get_test_db(client):
    """Get the testing DB session from the app's dependency override."""
    override = app.dependency_overrides.get(get_db)
    if override:
        gen = override()
        return next(gen)
    return None


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


def _create_subject(db) -> Subject:
    subj = Subject(name="Physics", slug="physics", category="Science")
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return subj


def _create_topic(db, subject_id: str = None) -> Topic:
    if subject_id is None:
        subj = _create_subject(db)
        subject_id = subj.id
    lesson = Lesson(subject_id=subject_id, title="Mechanics", slug="mechanics", content="Newtonian mechanics")
    db.add(lesson)
    db.commit()
    db.refresh(lesson)
    topic = Topic(lesson_id=lesson.id, title="Newton's Laws", content="Content about Newton's Laws of Motion")
    db.add(topic)
    db.commit()
    db.refresh(topic)
    return topic


def _create_flashcard(db, user_id: str, topic_id: str = None, question: str = "Q?", answer: str = "A.",
                      is_active: bool = True) -> Flashcard:
    card = Flashcard(user_id=user_id, topic_id=topic_id, question=question, answer=answer,
                     difficulty="medium", source="manual", is_active=is_active)
    db.add(card)
    db.commit()
    db.refresh(card)

    review = FlashcardReview(flashcard_id=card.id, ease_factor=2.5, interval_days=0, repetitions=0,
                             next_review_at=None)
    db.add(review)
    db.commit()
    db.refresh(card)
    return card


def _create_flashcard_and_review(db, user_id: str, topic_id: str, question: str, answer: str,
                                  next_review_at) -> Flashcard:
    card = Flashcard(user_id=user_id, topic_id=topic_id, question=question, answer=answer,
                     difficulty="medium", source="manual", is_active=True)
    db.add(card)
    db.commit()
    db.refresh(card)
    review = FlashcardReview(flashcard_id=card.id, ease_factor=2.5, interval_days=0, repetitions=0,
                             next_review_at=next_review_at)
    db.add(review)
    db.commit()
    db.refresh(card)
    return card


# ---------- get_flashcards ----------

def test_get_flashcards_empty(client: TestClient):
    resp = _signup(client, "fc_empty@test.com")
    token = _token(resp)

    response = client.get("/api/flashcards", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["flashcards"] == []
    assert data["total"] == 0


def test_get_flashcards_with_cards(client: TestClient):
    resp = _signup(client, "fc_with@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    _create_flashcard(db, uid, topic.id, "What is inertia?", "Inertia is...")
    _create_flashcard(db, uid, topic.id, "What is force?", "Force is...")
    db.close()

    response = client.get("/api/flashcards", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["flashcards"]) == 2


def test_get_flashcards_filter_by_topic_id(client: TestClient):
    resp = _signup(client, "fc_topicfilter@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic1 = _create_topic(db)
    topic2_id = "other-topic-id-for-testing"
    _create_flashcard(db, uid, topic1.id, "Q1", "A1")
    card2 = _create_flashcard(db, uid, topic1.id, "Q2", "A2")
    card3 = Flashcard(user_id=uid, topic_id=topic2_id, question="Q3", answer="A3",
                      difficulty="medium", source="manual", is_active=True)
    db.add(card3)
    db.commit()
    review3 = FlashcardReview(flashcard_id=card3.id, ease_factor=2.5, interval_days=0, repetitions=0,
                              next_review_at=None)
    db.add(review3)
    db.commit()
    topic1_id = topic1.id
    db.close()

    response = client.get(f"/api/flashcards?topic_id={topic1_id}", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2


def test_get_flashcards_filter_due_only(client: TestClient):
    resp = _signup(client, "fc_dueonly@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    _create_flashcard_and_review(db, uid, topic.id, "Due card", "Answer",
                                 next_review_at=datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=1))
    _create_flashcard_and_review(db, uid, topic.id, "Future card", "Answer",
                                 next_review_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(days=7))
    db.close()

    response = client.get("/api/flashcards?due_only=true", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert len(data["flashcards"]) == 1


# ---------- generate_flashcards ----------

def _mock_openai_response(text: str):
    mock_message = MagicMock()
    mock_message.content = text
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]
    return mock_completion


def test_generate_flashcards_success(client: TestClient, monkeypatch):
    resp = _signup(client, "fc_gen_ok@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    db.close()

    fake_flashcards = json.dumps([
        {"question": "What is Newton's first law?", "answer": "Inertia", "difficulty": "easy"},
        {"question": "What is force?", "answer": "Mass × acceleration", "difficulty": "medium"},
    ])

    import app.services.flashcard_service as fcs
    original_init = fcs.FlashcardService.__init__

    def mock_init(self, db):
        self.db = db
        self.openai = MagicMock()
        self.openai.chat.completions.create.return_value = _mock_openai_response(fake_flashcards)

    monkeypatch.setattr(fcs.FlashcardService, "__init__", mock_init)

    response = client.post("/api/flashcards/generate", headers=_auth_header(token), json={
        "topic_id": topic.id,
        "count": 2,
    })
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["flashcards"]) == 2
    assert data["flashcards"][0]["question"] == "What is Newton's first law?"

    monkeypatch.setattr(fcs.FlashcardService, "__init__", original_init)


def test_generate_flashcards_topic_not_found(client: TestClient, monkeypatch):
    resp = _signup(client, "fc_gen_notfound@test.com")
    token = _token(resp)

    import app.services.flashcard_service as fcs

    original_init = fcs.FlashcardService.__init__

    def mock_init(self, db):
        self.db = db
        self.openai = MagicMock()

    monkeypatch.setattr(fcs.FlashcardService, "__init__", mock_init)

    response = client.post("/api/flashcards/generate", headers=_auth_header(token), json={
        "topic_id": "nonexistent-topic-id",
        "count": 5,
    })
    assert response.status_code == 400
    assert "topic" in response.json()["detail"].lower() or "not found" in response.json()["detail"].lower()

    monkeypatch.setattr(fcs.FlashcardService, "__init__", original_init)


def test_generate_flashcards_no_api_key(client: TestClient, monkeypatch):
    resp = _signup(client, "fc_gen_nokey@test.com")
    token = _token(resp)

    db = _get_test_db(client)
    topic = _create_topic(db)
    db.close()

    import app.services.flashcard_service as fcs

    original_init = fcs.FlashcardService.__init__

    def mock_init(self, db):
        self.db = db
        self.openai = None

    monkeypatch.setattr(fcs.FlashcardService, "__init__", mock_init)

    response = client.post("/api/flashcards/generate", headers=_auth_header(token), json={
        "topic_id": topic.id,
        "count": 5,
    })
    assert response.status_code == 400
    assert "api key" in response.json()["detail"].lower()

    monkeypatch.setattr(fcs.FlashcardService, "__init__", original_init)


# ---------- review_flashcard ----------

def test_review_flashcard_quality_0(client: TestClient):
    resp = _signup(client, "fc_rev_0@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    db.close()

    response = client.post(f"/api/flashcards/{card.id}/review", headers=_auth_header(token), json={"quality": 0})
    assert response.status_code == 200
    data = response.json()
    assert data["interval_days"] == 1
    assert data["repetitions"] == 0


def test_review_flashcard_quality_5(client: TestClient):
    resp = _signup(client, "fc_rev_5@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    db.close()

    response = client.post(f"/api/flashcards/{card.id}/review", headers=_auth_header(token), json={"quality": 5})
    assert response.status_code == 200
    data = response.json()
    assert data["interval_days"] == 1
    assert data["repetitions"] == 1
    assert data["ease_factor"] > 2.5


def test_review_flashcard_quality_out_of_range(client: TestClient):
    resp = _signup(client, "fc_rev_oob@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    db.close()

    response = client.post(f"/api/flashcards/{card.id}/review", headers=_auth_header(token), json={"quality": 6})
    assert response.status_code == 400


def test_review_flashcard_not_found(client: TestClient):
    resp = _signup(client, "fc_rev_nf@test.com")
    token = _token(resp)

    response = client.post("/api/flashcards/nonexistent-id/review", headers=_auth_header(token), json={"quality": 3})
    assert response.status_code == 400


def test_review_flashcard_wrong_user(client: TestClient):
    resp1 = _signup(client, "fc_rev_owner@test.com")
    token1 = _token(resp1)
    uid1 = resp1["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid1, topic.id, "Q1", "A1")
    db.close()

    resp2 = _signup(client, "fc_rev_intruder@test.com")
    token2 = _token(resp2)

    response = client.post(f"/api/flashcards/{card.id}/review", headers=_auth_header(token2), json={"quality": 3})
    assert response.status_code == 400


def test_review_flashcard_quality_1_through_4(client: TestClient):
    resp = _signup(client, "fc_rev_1to4@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    db.close()

    for q in [1, 2, 3, 4]:
        response = client.post(f"/api/flashcards/{card.id}/review", headers=_auth_header(token), json={"quality": q})
        assert response.status_code == 200


# ---------- delete_flashcard ----------

def test_delete_flashcard_soft_delete(client: TestClient):
    resp = _signup(client, "fc_del_ok@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    db.close()

    response = client.delete(f"/api/flashcards/{card.id}", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["message"] == "Flashcard deleted"

    get_resp = client.get("/api/flashcards", headers=_auth_header(token))
    assert get_resp.json()["total"] == 0


def test_delete_flashcard_not_found(client: TestClient):
    resp = _signup(client, "fc_del_nf@test.com")
    token = _token(resp)

    response = client.delete("/api/flashcards/nonexistent-id", headers=_auth_header(token))
    assert response.status_code == 404


def test_delete_flashcard_already_inactive(client: TestClient):
    resp = _signup(client, "fc_del_inactive@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1", is_active=False)
    card_id = card.id
    db.close()

    response = client.delete(f"/api/flashcards/{card_id}", headers=_auth_header(token))
    assert response.status_code == 200


# ---------- Spaced repetition algorithm ----------

def test_spaced_repetition_first_review(client: TestClient):
    resp = _signup(client, "sr_first@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    card.review.interval_days = 0
    card.review.repetitions = 0
    card.review.ease_factor = 2.5
    db.commit()
    card_id = card.id
    db.close()

    response = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 4})
    assert response.status_code == 200
    data = response.json()
    assert data["interval_days"] == 1
    assert data["repetitions"] == 1


def test_spaced_repetition_second_review(client: TestClient):
    resp = _signup(client, "sr_second@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    card.review.interval_days = 1
    card.review.repetitions = 1
    card.review.ease_factor = 2.5
    db.commit()
    card_id = card.id
    db.close()

    response = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 4})
    assert response.status_code == 200
    data = response.json()
    assert data["interval_days"] == 6
    assert data["repetitions"] == 2


def test_spaced_repetition_third_review(client: TestClient):
    resp = _signup(client, "sr_third@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    card.review.interval_days = 6
    card.review.repetitions = 2
    card.review.ease_factor = 2.5
    db.commit()
    card_id = card.id
    db.close()

    response = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 4})
    assert response.status_code == 200
    data = response.json()
    expected_interval = round(6 * 2.5)
    assert data["interval_days"] == expected_interval
    assert data["repetitions"] == 3


def test_spaced_repetition_ease_factor_changes(client: TestClient):
    resp = _signup(client, "sr_ef@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    card.review.interval_days = 6
    card.review.repetitions = 2
    card.review.ease_factor = 2.5
    db.commit()
    card_id = card.id
    db.close()

    resp_quality_0 = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 0})
    ef_after_0 = resp_quality_0.json()["ease_factor"]
    assert ef_after_0 < 2.5

    resp_quality_5 = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 5})
    ef_after_5 = resp_quality_5.json()["ease_factor"]
    assert ef_after_5 > ef_after_0


# ---------- Edge cases ----------

def test_edge_quality_3_does_not_reset_interval(client: TestClient):
    resp = _signup(client, "edge_q3@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    card.review.interval_days = 10
    card.review.repetitions = 3
    card.review.ease_factor = 2.5
    db.commit()
    card_id = card.id
    db.close()

    response = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 3})
    data = response.json()
    expected_ef = round(2.5 + (0.1 - (5 - 3) * (0.08 + (5 - 3) * 0.02)), 2)
    expected_interval = round(10 * expected_ef)
    assert data["interval_days"] == expected_interval
    assert data["repetitions"] == 4


def test_edge_quality_5_max_interval_growth(client: TestClient):
    resp = _signup(client, "edge_q5@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    card.review.interval_days = 30
    card.review.repetitions = 5
    card.review.ease_factor = 2.5
    db.commit()
    card_id = card.id
    db.close()

    response = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 5})
    data = response.json()
    expected = round(30 * 2.5 + (0.1 - (5 - 5) * (0.08 + (5 - 5) * 0.02)))
    expected_ef = round(2.5 + (0.1 - (5 - 5) * (0.08 + (5 - 5) * 0.02)), 2)
    expected_interval = round(30 * expected_ef)
    assert data["interval_days"] == expected_interval
    assert data["repetitions"] == 6


def test_edge_quality_0_minimum_interval(client: TestClient):
    resp = _signup(client, "edge_q0@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    card.review.interval_days = 100
    card.review.repetitions = 10
    card.review.ease_factor = 3.0
    db.commit()
    card_id = card.id
    db.close()

    response = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 0})
    data = response.json()
    assert data["interval_days"] == 1
    assert data["repetitions"] == 0


def test_edge_repeating_same_flashcard(client: TestClient):
    resp = _signup(client, "edge_repeat@test.com")
    token = _token(resp)
    uid = resp["user"]["id"]

    db = _get_test_db(client)
    topic = _create_topic(db)
    card = _create_flashcard(db, uid, topic.id, "Q1", "A1")
    card_id = card.id
    db.close()

    r1 = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 4})
    d1 = r1.json()

    r2 = client.post(f"/api/flashcards/{card_id}/review", headers=_auth_header(token), json={"quality": 4})
    d2 = r2.json()

    assert d2["interval_days"] >= d1["interval_days"]
    assert d2["repetitions"] > d1["repetitions"]


def test_get_flashcards_unauthorized(client: TestClient):
    response = client.get("/api/flashcards")
    assert response.status_code == 401 or response.status_code == 403


def test_delete_flashcard_unauthorized(client: TestClient):
    response = client.delete("/api/flashcards/some-id")
    assert response.status_code == 401 or response.status_code == 403


def test_flashcards_isolation_between_users(client: TestClient):
    resp1 = _signup(client, "fc_iso1@test.com")
    token1 = _token(resp1)
    uid1 = resp1["user"]["id"]

    resp2 = _signup(client, "fc_iso2@test.com")
    token2 = _token(resp2)

    db = _get_test_db(client)
    topic = _create_topic(db)
    _create_flashcard(db, uid1, topic.id, "User1 card", "Answer 1")
    db.close()

    r1 = client.get("/api/flashcards", headers=_auth_header(token1))
    assert r1.json()["total"] == 1

    r2 = client.get("/api/flashcards", headers=_auth_header(token2))
    assert r2.json()["total"] == 0
