from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.repositories.base import BaseRepository
from typing import Optional


class SubjectRepository(BaseRepository[Subject]):
    def __init__(self, db: Session):
        super().__init__(Subject, db)

    def get_by_slug(self, slug: str) -> Optional[Subject]:
        query = select(self.model).where(self.model.slug == slug)
        return self.db.execute(query).scalar_one_or_none()

    def get_by_category(self, category: str) -> list[Subject]:
        query = select(self.model).where(self.model.category == category)
        return list(self.db.execute(query).scalars().all())
