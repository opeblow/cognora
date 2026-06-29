from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.lesson import Lesson, Topic
from app.repositories.base import BaseRepository


class LessonRepository(BaseRepository[Lesson]):
    def __init__(self, db: Session):
        super().__init__(Lesson, db)

    def get_by_subject(self, subject_id: str) -> list[Lesson]:
        query = select(self.model).where(
            self.model.subject_id == subject_id
        ).order_by(self.model.order_index)
        return list(self.db.execute(query).scalars().all())

    def get_by_slug(self, slug: str) -> Lesson | None:
        query = select(self.model).where(self.model.slug == slug)
        return self.db.execute(query).scalar_one_or_none()

    def get_topics(self, lesson_id: str) -> list[Topic]:
        from app.models.lesson import Topic
        query = select(Topic).where(
            Topic.lesson_id == lesson_id
        ).order_by(Topic.order_index)
        return list(self.db.execute(query).scalars().all())