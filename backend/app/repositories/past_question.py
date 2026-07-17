from typing import Optional
from sqlalchemy import select, func, distinct
from sqlalchemy.orm import Session
from app.models.past_question import PastQuestion
from app.repositories.base import BaseRepository
import random


class PastQuestionRepository(BaseRepository[PastQuestion]):
    def __init__(self, db: Session):
        super().__init__(PastQuestion, db)

    def get_all(
        self,
        board: Optional[str] = None,
        subject: Optional[str] = None,
        year: Optional[int] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[PastQuestion], int]:
        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        if board:
            query = query.where(self.model.exam_board == board)
            count_query = count_query.where(self.model.exam_board == board)
        if subject:
            query = query.where(self.model.subject == subject)
            count_query = count_query.where(self.model.subject == subject)
        if year:
            query = query.where(self.model.year == year)
            count_query = count_query.where(self.model.year == year)

        total = self.db.execute(count_query).scalar() or 0
        query = query.order_by(self.model.year.desc(), self.model.subject).offset(skip).limit(limit)
        items = list(self.db.execute(query).scalars().all())
        return items, total

    def get_random(
        self,
        board: Optional[str] = None,
        subject: Optional[str] = None,
        count: int = 20,
    ) -> list[PastQuestion]:
        query = select(self.model)

        if board:
            query = query.where(self.model.exam_board == board)
        if subject:
            query = query.where(self.model.subject == subject)

        rows = list(self.db.execute(query).scalars().all())
        random.shuffle(rows)
        return rows[:count]

    def get_boards(self) -> list[str]:
        query = select(distinct(self.model.exam_board))
        return [row[0] for row in self.db.execute(query).all()]

    def get_years(self, board: Optional[str] = None, subject: Optional[str] = None) -> list[int]:
        query = select(distinct(self.model.year))
        if board:
            query = query.where(self.model.exam_board == board)
        if subject:
            query = query.where(self.model.subject == subject)
        query = query.order_by(self.model.year.desc())
        return [row[0] for row in self.db.execute(query).all()]

    def get_subjects(self, board: Optional[str] = None) -> list[str]:
        query = select(distinct(self.model.subject))
        if board:
            query = query.where(self.model.exam_board == board)
        query = query.order_by(self.model.subject)
        return [row[0] for row in self.db.execute(query).all()]

    def seed_questions(self, data: list[dict]) -> list[PastQuestion]:
        instances = []
        for item in data:
            instance = self.model(**item)
            self.db.add(instance)
            instances.append(instance)
        try:
            self.db.commit()
            for inst in instances:
                self.db.refresh(inst)
        except Exception:
            self.db.rollback()
            raise
        return instances
