"""Extensible credit policy system.

Design:
- CreditPolicy is an abstract base class defining the interface.
- TrialCreditPolicy: grants free weekly credits, enforces trial limits.
- PaidCreditPolicy: works with purchased credits, no free grants.
- CreditService uses a policy instance — swap policies without changing core logic.
"""
from abc import ABC, abstractmethod
from typing import Optional
from app.models.user import User
from app.core.config import settings


class CreditPolicy(ABC):
    """Abstract base for credit policies. Implementations define how credits are granted and consumed."""

    @abstractmethod
    def get_available_credits(self, user: User) -> int:
        """Return the number of credits currently available to the user."""
        ...

    @abstractmethod
    def can_afford(self, user: User, cost: int) -> bool:
        """Return True if the user has enough credits for the given cost."""
        ...

    @abstractmethod
    def deduct(self, user: User, cost: int) -> dict:
        """Deduct credits and return a dict describing what was deducted and from which pool."""
        ...

    @abstractmethod
    def get_balance_details(self, user: User) -> dict:
        """Return a detailed breakdown of the user's credit state."""
        ...


class TrialCreditPolicy(CreditPolicy):
    """Free trial: users get a weekly allotment of credits at no cost."""

    def get_available_credits(self, user: User) -> int:
        return int(user.credits or 0)

    def can_afford(self, user: User, cost: int) -> bool:
        return (user.credits or 0) >= cost

    def deduct(self, user: User, cost: int) -> dict:
        user.credits = (user.credits or 0) - cost
        weekly = user.weekly_credits_used or 0
        user.weekly_credits_used = weekly + cost
        return {
            "deducted_from": "trial",
            "cost": cost,
            "remaining": user.credits or 0,
            "weekly_used": user.weekly_credits_used,
        }

    def get_balance_details(self, user: User) -> dict:
        return {
            "plan": "trial",
            "credits": int(user.credits or 0),
            "weekly_credits_used": int(user.weekly_credits_used or 0),
            "weekly_credits_total": settings.FREE_WEEKLY_CREDITS,
            "is_trial": True,
        }


class PaidCreditPolicy(CreditPolicy):
    """Paid plan: credits are purchased and consumed; no free weekly allotment."""

    def get_available_credits(self, user: User) -> int:
        return int(user.credits or 0)

    def can_afford(self, user: User, cost: int) -> bool:
        return (user.credits or 0) >= cost

    def deduct(self, user: User, cost: int) -> dict:
        user.credits = (user.credits or 0) - cost
        return {
            "deducted_from": "purchased",
            "cost": cost,
            "remaining": user.credits or 0,
        }

    def get_balance_details(self, user: User) -> dict:
        return {
            "plan": "paid",
            "credits": int(user.credits or 0),
            "is_trial": False,
        }
