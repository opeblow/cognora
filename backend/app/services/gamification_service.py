import logging
import math
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.gamification import Badge, UserBadge
from app.models.user_settings import UserSettings

logger = logging.getLogger(__name__)


XP_RATES = {
    "quiz_completed": 10,
    "exam_completed": 20,
    "lesson_completed": 5,
    "study_day_completed": 3,
    "streak_bonus": 2,
}

LEVEL_THRESHOLDS = [0, 100, 250, 500, 1000, 1750, 2750, 4000, 5500, 7500, 10000]


class GamificationService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, user: User) -> dict:
        next_xp = self._xp_for_level(user.level + 1)
        return {
            "total_xp": user.total_xp or 0,
            "level": user.level or 1,
            "current_streak": user.learning_streak or 0,
            "longest_streak": user.longest_streak or 0,
            "streak_freezes": user.streak_freezes or 0,
            "next_level_xp": next_xp,
            "xp_to_next_level": max(0, next_xp - (user.total_xp or 0)),
        }

    def update_streak(self, user: User) -> User:
        tz_name = self._get_user_timezone(user.id)
        now = datetime.now(timezone.utc)
        today_start = self._day_start(now, tz_name)

        if user.last_active_at is None:
            user.learning_streak = 1
            user.longest_streak = 1
        else:
            last_active = user.last_active_at
            last_day_start = self._day_start(last_active, tz_name)
            diff_days = (today_start - last_day_start).days

            if diff_days == 0:
                pass
            elif diff_days == 1:
                user.learning_streak = (user.learning_streak or 0) + 1
                if (user.learning_streak or 0) > (user.longest_streak or 0):
                    user.longest_streak = user.learning_streak
            else:
                if (user.streak_freezes or 0) > 0 and diff_days <= 3:
                    user.streak_freezes -= 1
                    user.learning_streak = (user.learning_streak or 0) + 1
                else:
                    user.learning_streak = 1

        user.last_active_at = now
        self.db.commit()
        self.db.refresh(user)
        return user

    def add_xp(self, user: User, base_xp: int, reason: str = "") -> dict:
        streak = user.learning_streak or 0
        streak_multiplier = min(streak, 10)
        bonus_xp = streak_multiplier * XP_RATES.get("streak_bonus", 2)
        total_xp_gain = base_xp + bonus_xp

        user.total_xp = (user.total_xp or 0) + total_xp_gain
        old_level = user.level or 1
        user.level = self._calculate_level(user.total_xp)
        leveled_up = user.level > old_level

        self.db.commit()
        self.db.refresh(user)

        awarded = self._check_badges(user)

        return {
            "xp_gained": total_xp_gain,
            "base_xp": base_xp,
            "streak_bonus": bonus_xp,
            "total_xp": user.total_xp,
            "level": user.level,
            "leveled_up": leveled_up,
            "badges_awarded": awarded,
        }

    def award_streak_freeze(self, user: User, amount: int = 1):
        user.streak_freezes = (user.streak_freezes or 0) + amount
        self.db.commit()

    def get_badges(self, user_id: str) -> list[dict]:
        results = (
            self.db.query(UserBadge, Badge)
            .join(Badge, UserBadge.badge_id == Badge.id)
            .filter(UserBadge.user_id == user_id)
            .order_by(UserBadge.awarded_at.desc())
            .all()
        )
        return [
            {
                "id": b.id,
                "name": b.name,
                "description": b.description,
                "icon": b.icon,
                "awarded_at": ub.awarded_at,
            }
            for ub, b in results
        ]

    def get_leaderboard(self, limit: int = 100) -> tuple[list[dict], int]:
        users = (
            self.db.query(User)
            .filter(User.is_active == True)
            .order_by(User.total_xp.desc())
            .limit(limit)
            .all()
        )
        total = (
            self.db.query(User)
            .filter(User.is_active == True)
            .count()
        )
        entries = [
            {
                "user_id": u.id,
                "full_name": u.full_name,
                "avatar_url": u.avatar_url,
                "total_xp": u.total_xp or 0,
                "level": u.level or 1,
                "rank": i + 1,
            }
            for i, u in enumerate(users)
        ]
        return entries, total

    def _get_user_timezone(self, user_id: str) -> str:
        settings = (
            self.db.query(UserSettings)
            .filter(UserSettings.user_id == user_id)
            .first()
        )
        return settings.timezone if settings and settings.timezone else "Africa/Lagos"

    def _day_start(self, dt: datetime, tz_name: str) -> datetime:
        try:
            import zoneinfo
            tz = zoneinfo.ZoneInfo(tz_name)
            local = dt.astimezone(tz)
            return datetime(local.year, local.month, local.day, tzinfo=tz)
        except Exception:
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    def _calculate_level(self, total_xp: int) -> int:
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if total_xp < threshold:
                return i
        return len(LEVEL_THRESHOLDS)

    def _xp_for_level(self, level: int) -> int:
        if level <= 1:
            return 0
        if level - 1 < len(LEVEL_THRESHOLDS):
            return LEVEL_THRESHOLDS[level - 1]
        return LEVEL_THRESHOLDS[-1] + (level - len(LEVEL_THRESHOLDS)) * 2000

    def _check_badges(self, user: User) -> list[str]:
        awarded = []
        badges = self.db.query(Badge).all()

        for badge in badges:
            already = (
                self.db.query(UserBadge)
                .filter(
                    UserBadge.user_id == user.id,
                    UserBadge.badge_id == badge.id,
                )
                .first()
            )
            if already:
                continue

            met = False
            if badge.criteria_type == "streak_reached":
                met = (user.learning_streak or 0) >= badge.criteria_value
            elif badge.criteria_type == "xp_earned":
                met = (user.total_xp or 0) >= badge.criteria_value
            elif badge.criteria_type == "quizzes_completed":
                count = len(user.quiz_attempts) if user.quiz_attempts else 0
                met = count >= badge.criteria_value
            elif badge.criteria_type == "level_reached":
                met = (user.level or 1) >= badge.criteria_value

            if met:
                ub = UserBadge(user_id=user.id, badge_id=badge.id)
                self.db.add(ub)
                self.db.flush()
                awarded.append(badge.name)

        if awarded:
            self.db.commit()

        return awarded
