from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.credit import CreditTransaction
from app.repositories.base import BaseRepository
from typing import Optional
from datetime import datetime, timezone, timedelta


class CreditTransactionRepository(BaseRepository[CreditTransaction]):
    def __init__(self, db: Session):
        super().__init__(CreditTransaction, db)

    def get_by_user(self, user_id: str, limit: int = 50) -> list[CreditTransaction]:
        query = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(self.model.created_at.desc()).limit(limit)
        return list(self.db.execute(query).scalars().all())

    def get_weekly_usage(self, user_id: str) -> int:
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        query = select(func.sum(self.model.amount)).where(
            self.model.user_id == user_id,
            self.model.transaction_type == "usage",
            self.model.created_at >= week_ago
        )
        result = self.db.execute(query).scalar()
        return abs(result or 0)
