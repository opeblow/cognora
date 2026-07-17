from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from app.models.study_group import StudyGroup, StudyGroupMember, StudyGroupMessage
from app.models.user import User
from app.repositories.base import BaseRepository
from typing import Optional


class StudyGroupRepository(BaseRepository[StudyGroup]):
    def __init__(self, db: Session):
        super().__init__(StudyGroup, db)

    def get_by_user(self, user_id: str) -> list[StudyGroup]:
        query = (
            select(StudyGroup)
            .join(StudyGroupMember, StudyGroupMember.group_id == StudyGroup.id)
            .where(
                StudyGroupMember.user_id == user_id,
                StudyGroup.is_active == True,
            )
            .order_by(StudyGroup.created_at.desc())
        )
        return list(self.db.execute(query).scalars().all())

    def get_public(self, subject: Optional[str] = None) -> list[StudyGroup]:
        query = select(StudyGroup).where(StudyGroup.is_active == True)
        if subject:
            query = query.where(StudyGroup.subject == subject)
        query = query.order_by(StudyGroup.created_at.desc())
        return list(self.db.execute(query).scalars().all())

    def get_with_members(self, group_id: str) -> Optional[StudyGroup]:
        query = (
            select(StudyGroup)
            .options(
                joinedload(StudyGroup.members).joinedload(StudyGroupMember.user),
                joinedload(StudyGroup.creator),
            )
            .where(StudyGroup.id == group_id)
        )
        return self.db.execute(query).unique().scalar_one_or_none()

    def is_member(self, group_id: str, user_id: str) -> bool:
        query = select(StudyGroupMember).where(
            StudyGroupMember.group_id == group_id,
            StudyGroupMember.user_id == user_id,
        )
        return self.db.execute(query).scalar_one_or_none() is not None

    def add_member(self, group_id: str, user_id: str, role: str = "member") -> StudyGroupMember:
        member = StudyGroupMember(
            group_id=group_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(member)
        self.db.commit()
        self.db.refresh(member)
        return member

    def remove_member(self, group_id: str, user_id: str) -> bool:
        query = select(StudyGroupMember).where(
            StudyGroupMember.group_id == group_id,
            StudyGroupMember.user_id == user_id,
        )
        member = self.db.execute(query).scalar_one_or_none()
        if not member:
            return False
        self.db.delete(member)
        self.db.commit()
        return True

    def get_member_count(self, group_id: str) -> int:
        query = select(func.count()).where(StudyGroupMember.group_id == group_id)
        return self.db.execute(query).scalar() or 0

    def get_messages(self, group_id: str, limit: int = 50, offset: int = 0) -> list[StudyGroupMessage]:
        query = (
            select(StudyGroupMessage)
            .where(StudyGroupMessage.group_id == group_id)
            .order_by(StudyGroupMessage.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.execute(query).scalars().all())

    def get_messages_count(self, group_id: str) -> int:
        query = select(func.count()).where(StudyGroupMessage.group_id == group_id)
        return self.db.execute(query).scalar() or 0

    def add_message(self, group_id: str, user_id: str, content: str) -> StudyGroupMessage:
        msg = StudyGroupMessage(
            group_id=group_id,
            user_id=user_id,
            content=content,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg
