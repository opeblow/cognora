from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from app.repositories.credit import CreditTransactionRepository
from app.repositories.user import UserRepository
from app.core.config import settings


class CreditService:
    CREDIT_COSTS = {
        "ai_ask": 1,
        "generate_quiz": 2,
        "mock_exam": 10,
    }

    def __init__(self, db: Session):
        self.credit_repo = CreditTransactionRepository(db)
        self.user_repo = UserRepository(db)
        self.db = db

    def get_balance(self, user_id: str) -> dict:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        self._reset_weekly_if_needed(user)

        weekly_used = self.credit_repo.get_weekly_usage(user_id)
        transactions = self.credit_repo.get_by_user(user_id)

        return {
            "credits": user.credits or 0,
            "weekly_credits_used": weekly_used,
            "weekly_credits_total": settings.FREE_WEEKLY_CREDITS,
            "transactions": [
                {
                    "id": str(t.id),
                    "amount": t.amount,
                    "transaction_type": t.transaction_type,
                    "description": t.description,
                    "created_at": t.created_at.isoformat() if t.created_at else None
                }
                for t in transactions
            ]
        }

    def _reset_weekly_if_needed(self, user):
        now = datetime.utcnow()
        if user.weekly_credits_reset_at:
            reset_at = user.weekly_credits_reset_at
            if hasattr(reset_at, 'tzinfo') and reset_at.tzinfo is not None:
                reset_at = reset_at.replace(tzinfo=None)
            if reset_at < now:
                user.weekly_credits_used = 0
                user.weekly_credits_reset_at = now + timedelta(days=7)
                self.db.commit()

    def deduct_credits(self, user_id: str, action: str) -> bool:
        cost = self.CREDIT_COSTS.get(action)
        if cost is None:
            raise ValueError(f"Unknown action: {action}")

        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        self._reset_weekly_if_needed(user)

        current_credits = user.credits or 0
        if current_credits < cost:
            raise ValueError("Insufficient credits")

        user.credits = current_credits - cost
        weekly_used = user.weekly_credits_used or 0
        user.weekly_credits_used = weekly_used + cost

        self.credit_repo.create(
            user_id=user.id,
            amount=-cost,
            transaction_type="usage",
            description=f"Used {cost} credits for {action}"
        )

        self.db.commit()
        return True

    def add_credits(self, user_id: str, amount: int, description: str) -> bool:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        current = user.credits or 0
        user.credits = current + amount

        self.credit_repo.create(
            user_id=user.id,
            amount=amount,
            transaction_type="purchase",
            description=description
        )

        self.db.commit()
        return True
