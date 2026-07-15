from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import update, func
from app.repositories.credit import CreditTransactionRepository
from app.repositories.user import UserRepository
from app.core.config import settings
from app.models.user import User
from app.services.credit_policy import CreditPolicy, TrialCreditPolicy, PaidCreditPolicy


class CreditService:
    CREDIT_COSTS = {
        "ai_ask": 1,
        "generate_quiz": 2,
        "mock_exam": 10,
    }

    def __init__(self, db: Session, policy: Optional[CreditPolicy] = None):
        self.credit_repo = CreditTransactionRepository(db)
        self.user_repo = UserRepository(db)
        self.db = db
        self.policy = policy or TrialCreditPolicy()

    def set_policy(self, policy: CreditPolicy):
        """Swap the credit policy at runtime (e.g., after a purchase)."""
        self.policy = policy

    def get_balance(self, user_id: str) -> dict:
        user = self.user_repo.get(user_id)
        if not user:
            raise ValueError("User not found")

        self._reset_weekly_if_needed(user)

        transactions = self.credit_repo.get_by_user(user_id)

        balance = self.policy.get_balance_details(user)
        balance["transactions"] = [
            {
                "id": str(t.id),
                "amount": t.amount,
                "transaction_type": t.transaction_type,
                "description": t.description,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ]
        return balance

    def deduct_credits(self, user_id: str, action: str) -> bool:
        cost = self.CREDIT_COSTS.get(action)
        if cost is None:
            raise ValueError(f"Unknown action: {action}")

        # A conditional UPDATE prevents concurrent requests from overspending.
        updated = self.db.execute(
            update(User)
            .where(User.id == user_id, User.credits >= cost)
            .values(credits=User.credits - cost, weekly_credits_used=User.weekly_credits_used + cost)
        ).rowcount
        if not updated:
            user = self.user_repo.get(user_id)
            if not user:
                raise ValueError("User not found")
            remaining = self.policy.get_available_credits(user)
            raise ValueError(
                f"Insufficient credits. You need {cost} credits but have {remaining}. "
                f"Please top up to continue. "
                f'{{"action": "upgrade_to_premium", "required": {cost}, "available": {remaining}}}'
            )

        self.db.add(self.credit_repo.model(
            user_id=user_id,
            amount=-cost,
            transaction_type="usage",
            description=f"Used {cost} credits for {action}",
        ))

        self.db.commit()
        return True

    def add_credits(self, user_id: str, amount: int, description: str = "") -> bool:
        updated = self.db.execute(update(User).where(User.id == user_id).values(credits=User.credits + amount)).rowcount
        if not updated:
            raise ValueError("User not found")
        self.db.add(self.credit_repo.model(
            user_id=user_id,
            amount=amount,
            transaction_type="purchase",
            description=description or f"Purchased {amount} credits",
        ))

        self.db.commit()
        return True

    def award_trial_bonus(self, user_id: str) -> bool:
        """Grant first-time trial credits on signup (atomic — safe for concurrent calls)."""
        now = datetime.now(timezone.utc)
        trial_amount = settings.FREE_WEEKLY_CREDITS
        updated = self.db.execute(
            update(User)
            .where(User.id == user_id, (User.credits == 0) | (User.credits.is_(None)))
            .values(
                credits=trial_amount,
                weekly_credits_used=0,
                weekly_credits_reset_at=now + timedelta(days=7),
            )
        ).rowcount
        if not updated:
            return False

        self.credit_repo.create(
            user_id=user_id,
            amount=trial_amount,
            transaction_type="bonus",
            description=f"Free trial: {trial_amount} credits granted",
        )
        self.db.commit()
        return True

    def _reset_weekly_if_needed(self, user):
        now = datetime.now(timezone.utc)
        if not user.weekly_credits_reset_at:
            return
        reset_at = user.weekly_credits_reset_at
        if reset_at.tzinfo is None:
            reset_at = reset_at.replace(tzinfo=timezone.utc)
        if reset_at >= now:
            return

        new_reset = now + timedelta(days=7)
        if isinstance(self.policy, TrialCreditPolicy):
            updated = self.db.execute(
                update(User)
                .where(User.id == user.id, User.weekly_credits_reset_at == user.weekly_credits_reset_at)
                .values(
                    weekly_credits_used=0,
                    weekly_credits_reset_at=new_reset,
                    credits=User.credits + settings.FREE_WEEKLY_CREDITS,
                )
            ).rowcount
            if not updated:
                return
            self.credit_repo.create(
                user_id=user.id,
                amount=settings.FREE_WEEKLY_CREDITS,
                transaction_type="bonus",
                description=f"Weekly free credits: {settings.FREE_WEEKLY_CREDITS} granted",
            )
        else:
            updated = self.db.execute(
                update(User)
                .where(User.id == user.id, User.weekly_credits_reset_at == user.weekly_credits_reset_at)
                .values(
                    weekly_credits_used=0,
                    weekly_credits_reset_at=new_reset,
                )
            ).rowcount
            if not updated:
                return

        self.db.commit()

    def get_policy(self) -> str:
        if isinstance(self.policy, PaidCreditPolicy):
            return "paid"
        return "trial"
