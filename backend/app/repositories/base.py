from typing import Generic, TypeVar, Type, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.database.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def create(self, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        self.db.add(instance)
        try:
            self.db.commit()
            self.db.refresh(instance)
        except Exception:
            self.db.rollback()
            raise
        return instance

    def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        return self.db.execute(query).scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100, **filters) -> tuple[list[ModelType], int]:
        query = select(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.where(getattr(self.model, key) == value)
        count_query = select(func.count()).select_from(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                count_query = count_query.where(getattr(self.model, key) == value)
        total = self.db.execute(count_query).scalar() or 0
        query = query.order_by(self.model.id).offset(skip).limit(limit)
        items = list(self.db.execute(query).scalars().all())
        return items, total

    def update(self, id: Any, **kwargs) -> Optional[ModelType]:
        instance = self.get(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        try:
            self.db.commit()
            self.db.refresh(instance)
        except Exception:
            self.db.rollback()
            raise
        return instance

    def delete(self, id: Any) -> bool:
        instance = self.get(id)
        if not instance:
            return False
        self.db.delete(instance)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return True
