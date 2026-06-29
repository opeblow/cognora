from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models.exam import Exam, ExamQuestion, ExamResult, ExamAnswer
from app.repositories.base import BaseRepository
from typing import Optional


class ExamRepository(BaseRepository[Exam]):
    def __init__(self, db: Session):
        super().__init__(Exam, db)

    def get_with_questions(self, id) -> Optional[Exam]:
        query = select(self.model).where(self.model.id == id).options(joinedload(self.model.questions))
        return self.db.execute(query).unique().scalar_one_or_none()

    def get_by_subject(self, subject_id: str) -> list[Exam]:
        query = select(self.model).where(self.model.subject_id == subject_id)
        return list(self.db.execute(query).scalars().all())

    def get_by_type(self, exam_type: str) -> list[Exam]:
        query = select(self.model).where(self.model.exam_type == exam_type)
        return list(self.db.execute(query).scalars().all())


class ExamResultRepository(BaseRepository[ExamResult]):
    def __init__(self, db: Session):
        super().__init__(ExamResult, db)

    def get_by_user(self, user_id: str) -> list[ExamResult]:
        query = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(self.model.started_at.desc())
        return list(self.db.execute(query).scalars().all())

    def get_in_progress(self, user_id: str, exam_id: str) -> Optional[ExamResult]:
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.exam_id == exam_id,
            self.model.status == "in_progress"
        )
        return self.db.execute(query).scalar_one_or_none()
