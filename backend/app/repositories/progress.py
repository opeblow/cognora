from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.progress import UserProgress
from app.repositories.base import BaseRepository
from typing import Optional


class UserProgressRepository(BaseRepository[UserProgress]):
    def __init__(self, db: Session):
        super().__init__(UserProgress, db)

    def get_by_user_and_subject(self, user_id: str, subject_id: str) -> Optional[UserProgress]:
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.subject_id == subject_id
        )
        return self.db.execute(query).scalar_one_or_none()

    def get_by_user(self, user_id: str) -> list[UserProgress]:
        query = select(self.model).where(self.model.user_id == user_id)
        return list(self.db.execute(query).scalars().all())
