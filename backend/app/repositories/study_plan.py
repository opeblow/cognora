from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models.study_plan import StudyPlan, StudyPlanDay
from app.repositories.base import BaseRepository
from typing import Optional
from datetime import date


class StudyPlanRepository(BaseRepository[StudyPlan]):
    def __init__(self, db: Session):
        super().__init__(StudyPlan, db)

    def get_with_days(self, plan_id: str) -> Optional[StudyPlan]:
        query = select(self.model).where(self.model.id == plan_id).options(
            joinedload(self.model.days)
        )
        return self.db.execute(query).unique().scalar_one_or_none()

    def get_by_user(self, user_id: str) -> list[StudyPlan]:
        query = select(self.model).where(
            self.model.user_id == user_id
        ).order_by(self.model.created_at.desc())
        return list(self.db.execute(query).scalars().all())

    def get_active_plans(self, user_id: str) -> list[StudyPlan]:
        query = select(self.model).where(
            self.model.user_id == user_id,
            self.model.is_active == "true"
        ).order_by(self.model.start_date)
        return list(self.db.execute(query).scalars().all())

    def add_day(self, plan_id: str, **kwargs) -> StudyPlanDay:
        day = StudyPlanDay(study_plan_id=plan_id, **kwargs)
        self.db.add(day)
        self.db.commit()
        self.db.refresh(day)
        return day

    def get_day(self, day_id: str) -> Optional[StudyPlanDay]:
        query = select(StudyPlanDay).where(StudyPlanDay.id == day_id)
        return self.db.execute(query).scalar_one_or_none()

    def get_days_in_range(self, user_id: str, start: date, end: date) -> list[StudyPlanDay]:
        query = (
            select(StudyPlanDay)
            .join(StudyPlan, StudyPlan.id == StudyPlanDay.study_plan_id)
            .where(
                StudyPlan.user_id == user_id,
                StudyPlanDay.date >= start,
                StudyPlanDay.date <= end,
            )
            .order_by(StudyPlanDay.date)
        )
        return list(self.db.execute(query).scalars().all())
