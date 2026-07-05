import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.database.base import get_db
from app.main import app
from app.models.user import User
from app.models.gamification import Badge, UserBadge
from app.models.user_settings import UserSettings
from app.services.gamification_service import GamificationService, XP_RATES, LEVEL_THRESHOLDS


def _signup(client: TestClient, email: str) -> dict:
    resp = client.post("/api/auth/signup", json={
        "email": f"gami_{email}@example.com",
        "password": "TestPass123!",
        "full_name": f"Gami {email}",
    })
    return resp.json()


def _get_user(db, user_id: str) -> User:
    return db.query(User).filter(User.id == user_id).first()


def _test_db():
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    return db, gen


def test_get_profile_initial_state(client: TestClient):
    user = _signup(client, "init")
    token = user["access_token"]
    resp = client.get("/api/gamification/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_xp"] == 0
    assert data["level"] == 1
    assert data["current_streak"] == 0
    assert data["streak_freezes"] == 0


def test_get_profile_after_xp_gain(client: TestClient):
    udata = _signup(client, "afterxp")
    db, gen = _test_db()
    try:
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        svc.add_xp(u, 50, "test")
    finally:
        gen.close()

    token = udata["access_token"]
    resp = client.get("/api/gamification/profile", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_xp"] >= 50
    assert data["level"] >= 1


def test_get_badges_empty(client: TestClient):
    user = _signup(client, "bempty")
    token = user["access_token"]
    resp = client.get("/api/gamification/badges", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_badges_with_badges(client: TestClient):
    udata = _signup(client, "bwith")
    db, gen = _test_db()
    try:
        u = _get_user(db, udata["user"]["id"])
        badge = Badge(name="Test Badge", description="A test", icon="star", criteria_type="xp_earned", criteria_value=10)
        db.add(badge)
        db.flush()
        ub = UserBadge(user_id=u.id, badge_id=badge.id)
        db.add(ub)
        db.commit()
    finally:
        gen.close()

    token = udata["access_token"]
    resp = client.get("/api/gamification/badges", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    badges = resp.json()
    assert len(badges) == 1
    assert badges[0]["name"] == "Test Badge"


def test_get_leaderboard_empty(client: TestClient):
    resp = client.get("/api/gamification/leaderboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["entries"] == []
    assert data["total_count"] == 0


def test_get_leaderboard_with_users(client: TestClient):
    for i in range(3):
        _signup(client, f"lb_user{i}")

    db, gen = _test_db()
    try:
        for u in db.query(User).order_by(User.created_at.desc()).limit(3).all():
            u.total_xp = 100
        db.commit()
    finally:
        gen.close()

    resp = client.get("/api/gamification/leaderboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_count"] >= 3


def test_leaderboard_ranking_order(client: TestClient):
    db, gen = _test_db()
    uids = []
    try:
        for i in range(3):
            udata = _signup(client, f"rank_user{i}")
            uid = udata["user"]["id"]
            uids.append(uid)
        u1 = _get_user(db, uids[0])
        u1.total_xp = 300
        u2 = _get_user(db, uids[1])
        u2.total_xp = 100
        u3 = _get_user(db, uids[2])
        u3.total_xp = 200
        db.commit()
    finally:
        gen.close()

    resp = client.get("/api/gamification/leaderboard?limit=10")
    entries = resp.json()["entries"]
    xps = [e["total_xp"] for e in entries if e["user_id"] in uids]
    assert xps == sorted(xps, reverse=True)


def test_update_streak_first_activity(client: TestClient):
    udata = _signup(client, "streak_first")
    db, gen = _test_db()
    try:
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        svc.update_streak(u)
        assert u.learning_streak == 1
        assert u.longest_streak == 1
    finally:
        gen.close()


def test_update_streak_consecutive_day(client: TestClient):
    udata = _signup(client, "streak_cons")
    db, gen = _test_db()
    try:
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        svc.update_streak(u)
        assert u.learning_streak == 1
        u.last_active_at = datetime.now(timezone.utc) - timedelta(days=1)
        db.commit()
        svc.update_streak(u)
        assert u.learning_streak >= 2
    finally:
        gen.close()


def test_update_streak_same_day_no_increment(client: TestClient):
    udata = _signup(client, "streak_same")
    db, gen = _test_db()
    try:
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        svc.update_streak(u)
        streak_before = u.learning_streak
        svc.update_streak(u)
        assert u.learning_streak == streak_before
    finally:
        gen.close()


def test_update_streak_missed_day_breaks_streak(client: TestClient):
    udata = _signup(client, "streak_break")
    db, gen = _test_db()
    try:
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.last_active_at = datetime.now(timezone.utc) - timedelta(days=5)
        db.commit()
        svc.update_streak(u)
        assert u.learning_streak == 1
    finally:
        gen.close()


def test_update_streak_freeze_used(client: TestClient):
    udata = _signup(client, "streak_freeze")
    db, gen = _test_db()
    try:
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.streak_freezes = 2
        u.learning_streak = 5
        u.last_active_at = datetime.now(timezone.utc) - timedelta(days=2)
        u.longest_streak = 5
        db.commit()
        svc.update_streak(u)
        assert u.streak_freezes == 1
        assert u.learning_streak == 6
    finally:
        gen.close()


def test_update_streak_freeze_exhausted(client: TestClient):
    udata = _signup(client, "streak_freeze_gone")
    db, gen = _test_db()
    try:
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.streak_freezes = 0
        u.learning_streak = 10
        u.longest_streak = 10
        u.last_active_at = datetime.now(timezone.utc) - timedelta(days=3)
        db.commit()
        svc.update_streak(u)
        assert u.learning_streak == 1
    finally:
        gen.close()


def test_add_xp_base_only(client: TestClient):
    db, gen = _test_db()
    try:
        udata = _signup(client, "xp_base")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        result = svc.add_xp(u, 10, "quiz_completed")
        assert result["base_xp"] == 10
        assert result["xp_gained"] >= 10
        assert u.total_xp >= 10
    finally:
        gen.close()


def test_add_xp_streak_bonus(client: TestClient):
    db, gen = _test_db()
    try:
        udata = _signup(client, "xp_bonus")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.learning_streak = 5
        db.commit()
        result = svc.add_xp(u, 10, "quiz_completed")
        expected_bonus = min(5, 10) * XP_RATES["streak_bonus"]
        assert result["streak_bonus"] == expected_bonus
        assert result["xp_gained"] == 10 + expected_bonus
    finally:
        gen.close()


def test_add_xp_level_up(client: TestClient):
    db, gen = _test_db()
    try:
        udata = _signup(client, "xp_levelup")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.total_xp = 95
        u.level = 1
        db.commit()
        result = svc.add_xp(u, 10, "quiz_completed")
        assert result["leveled_up"] is True
        assert result["level"] >= 2
    finally:
        gen.close()


def test_add_xp_no_level_up(client: TestClient):
    db, gen = _test_db()
    try:
        udata = _signup(client, "xp_nolevel")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.total_xp = 0
        u.level = 1
        db.commit()
        result = svc.add_xp(u, 5, "lesson_completed")
        assert result["leveled_up"] is False
        assert result["level"] == 1
    finally:
        gen.close()


def test_xp_rates_mapping():
    assert XP_RATES["quiz_completed"] == 10
    assert XP_RATES["exam_completed"] == 20
    assert XP_RATES["lesson_completed"] == 5
    assert XP_RATES["study_day_completed"] == 3
    assert XP_RATES["streak_bonus"] == 2


def test_level_calculation_boundary(client: TestClient):
    db, gen = _test_db()
    try:
        svc = GamificationService(db)
        assert svc._calculate_level(0) == 1
        assert svc._calculate_level(99) == 1
        assert svc._calculate_level(100) == 2
        assert svc._calculate_level(249) == 2
        assert svc._calculate_level(250) == 3
        assert svc._calculate_level(9999) == 10
        assert svc._calculate_level(10000) == 11
        assert svc._calculate_level(20000) == 11
    finally:
        gen.close()


def test_xp_for_level_function(client: TestClient):
    db, gen = _test_db()
    try:
        svc = GamificationService(db)
        assert svc._xp_for_level(1) == 0
        assert svc._xp_for_level(2) == LEVEL_THRESHOLDS[1]
        assert svc._xp_for_level(11) == LEVEL_THRESHOLDS[-1]
        assert svc._xp_for_level(12) == LEVEL_THRESHOLDS[-1] + 2000
    finally:
        gen.close()


def test_max_level(client: TestClient):
    db, gen = _test_db()
    try:
        udata = _signup(client, "max_lvl")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.total_xp = 50000
        db.commit()
        result = svc.add_xp(u, 100, "exam_completed")
        assert result["level"] == 11
    finally:
        gen.close()


def test_very_high_xp(client: TestClient):
    db, gen = _test_db()
    try:
        udata = _signup(client, "high_xp")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.total_xp = 10**9
        db.commit()
        svc.update_streak(u)
        result = svc.add_xp(u, 100, "exam_completed")
        assert result["level"] == 11
    finally:
        gen.close()


def test_badge_criteria_streak_reached(client: TestClient):
    db, gen = _test_db()
    try:
        badge = Badge(name="Streak Master", criteria_type="streak_reached", criteria_value=3)
        db.add(badge)
        db.commit()

        udata = _signup(client, "badge_streak")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.learning_streak = 3
        db.commit()
        awarded = svc._check_badges(u)
        assert "Streak Master" in awarded
    finally:
        gen.close()


def test_badge_criteria_xp_earned(client: TestClient):
    db, gen = _test_db()
    try:
        badge = Badge(name="XP Hunter", criteria_type="xp_earned", criteria_value=500)
        db.add(badge)
        db.commit()

        udata = _signup(client, "badge_xp")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.total_xp = 600
        db.commit()
        awarded = svc._check_badges(u)
        assert "XP Hunter" in awarded
    finally:
        gen.close()


def test_badge_criteria_level_reached(client: TestClient):
    db, gen = _test_db()
    try:
        badge = Badge(name="Level Up!", criteria_type="level_reached", criteria_value=5)
        db.add(badge)
        db.commit()

        udata = _signup(client, "badge_lvl")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.level = 5
        db.commit()
        awarded = svc._check_badges(u)
        assert "Level Up!" in awarded
    finally:
        gen.close()


def test_badge_already_awarded_skipped(client: TestClient):
    badge_id = None
    db1, gen1 = _test_db()
    try:
        badge = Badge(name="Unique Badge", criteria_type="xp_earned", criteria_value=10)
        db1.add(badge)
        db1.flush()
        badge_id = badge.id
        db1.commit()
    finally:
        gen1.close()

    udata = _signup(client, "badge_dup")

    db2, gen2 = _test_db()
    try:
        u = _get_user(db2, udata["user"]["id"])
        ub = UserBadge(user_id=u.id, badge_id=badge_id)
        db2.add(ub)
        db2.commit()
    finally:
        gen2.close()

    db3, gen3 = _test_db()
    try:
        svc = GamificationService(db3)
        u = _get_user(db3, udata["user"]["id"])
        u.total_xp = 100
        db3.commit()
        awarded = svc._check_badges(u)
        assert "Unique Badge" not in awarded
    finally:
        gen3.close()


def test_award_streak_freeze(client: TestClient):
    db, gen = _test_db()
    try:
        udata = _signup(client, "freeze_award")
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        svc.award_streak_freeze(u, 3)
        assert u.streak_freezes == 3
    finally:
        gen.close()


def test_get_profile_step_by_step(client: TestClient):
    udata = _signup(client, "pro_step")
    db, gen = _test_db()
    try:
        u = _get_user(db, udata["user"]["id"])
        svc = GamificationService(db)
        u.learning_streak = 7
        u.longest_streak = 10
        u.streak_freezes = 2
        u.total_xp = 150
        u.level = 2
        db.commit()
    finally:
        gen.close()

    token = udata["access_token"]
    resp = client.get("/api/gamification/profile", headers={"Authorization": f"Bearer {token}"})
    d = resp.json()
    assert d["current_streak"] == 7
    assert d["longest_streak"] == 10
    assert d["streak_freezes"] == 2
    assert d["total_xp"] == 150
    assert d["level"] == 2
