from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models.quiz import Quiz, Question, QuizAttempt, QuizAnswer
from app.repositories.base import BaseRepository
from typing import Optional


class QuizRepository(BaseRepository[Quiz]):
    def __init__(self, db: Session):
        super().__init__(Quiz, db)

    def get_with_questions(self, id) -> Optional[Quiz]:
        query = select(self.model).where(self.model.id == id).options(joinedload(self.model.questions))
        return self.db.execute(query).unique().scalar_one_or_none()

    def get_by_subject(self, subject_id: str) -> list[Quiz]:
        query = select(self.model).where(self.model.subject_id == subject_id)
        return list(self.db.execute(query).scalars().all())


class QuestionRepository(BaseRepository[Question]):
    def __init__(self, db: Session):
        super().__init__(Question, db)


class QuizAttemptRepository(BaseRepository[QuizAttempt]):
    def __init__(self, db: Session):
        super().__init__(QuizAttempt, db)

    def get_by_user_and_quiz(self, user_id: str, quiz_id: str) -> list[QuizAttempt]:
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.quiz_id == quiz_id
        )
        return list(self.db.execute(query).scalars().all())

    def get_by_user(self, user_id: str) -> list[QuizAttempt]:
        query = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(self.model.created_at.desc())
        return list(self.db.execute(query).scalars().all())
