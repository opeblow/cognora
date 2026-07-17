import logging
from typing import Optional
from sqlalchemy.orm import Session
from app.models.study_group import StudyGroup
from app.repositories.study_group import StudyGroupRepository
from app.models.user import User

logger = logging.getLogger(__name__)


class StudyGroupService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = StudyGroupRepository(db)

    def create_group(
        self, user_id: str, name: str,
        subject: Optional[str] = None,
        description: Optional[str] = None,
        max_members: int = 10,
    ) -> StudyGroup:
        group = self.repo.create(
            name=name,
            subject=subject,
            description=description,
            creator_id=user_id,
            max_members=max_members,
            is_active=True,
        )
        self.repo.add_member(group.id, user_id, role="admin")
        return group

    def join_group(self, group_id: str, user_id: str) -> dict:
        group = self.repo.get(group_id)
        if not group or not group.is_active:
            return {"error": "Group not found or inactive"}

        if self.repo.is_member(group_id, user_id):
            return {"error": "Already a member"}

        member_count = self.repo.get_member_count(group_id)
        if member_count >= group.max_members:
            return {"error": "Group is full"}

        self.repo.add_member(group_id, user_id)
        return {"message": "Joined group", "group_id": group_id}

    def leave_group(self, group_id: str, user_id: str) -> dict:
        group = self.repo.get(group_id)
        if not group:
            return {"error": "Group not found"}

        if not self.repo.is_member(group_id, user_id):
            return {"error": "Not a member"}

        self.repo.remove_member(group_id, user_id)

        remaining = self.repo.get_member_count(group_id)
        if remaining == 0:
            self.repo.update(group_id, is_active=False)

        return {"message": "Left group", "group_id": group_id}

    def get_user_groups(self, user_id: str) -> list[StudyGroup]:
        return self.repo.get_by_user(user_id)

    def browse_groups(self, subject: Optional[str] = None) -> list[StudyGroup]:
        return self.repo.get_public(subject)

    def get_group_detail(self, group_id: str) -> Optional[StudyGroup]:
        return self.repo.get_with_members(group_id)

    def send_message(self, group_id: str, user_id: str, content: str):
        group = self.repo.get(group_id)
        if not group or not group.is_active:
            return {"error": "Group not found or inactive"}

        if not self.repo.is_member(group_id, user_id):
            return {"error": "Not a member"}

        msg = self.repo.add_message(group_id, user_id, content)
        return {
            "id": msg.id,
            "group_id": msg.group_id,
            "user_id": msg.user_id,
            "content": msg.content,
            "created_at": msg.created_at,
        }

    def get_messages(self, group_id: str, user_id: str, offset: int = 0, limit: int = 50):
        group = self.repo.get(group_id)
        if not group or not group.is_active:
            return {"error": "Group not found or inactive"}

        if not self.repo.is_member(group_id, user_id):
            return {"error": "Not a member"}

        messages = self.repo.get_messages(group_id, limit, offset)
        total = self.repo.get_messages_count(group_id)
        return {"messages": messages, "total": total}

    def delete_group(self, group_id: str, user_id: str) -> dict:
        group = self.repo.get(group_id)
        if not group:
            return {"error": "Group not found"}

        if group.creator_id != user_id:
            return {"error": "Only the creator can delete this group"}

        self.repo.update(group_id, is_active=False)
        return {"message": "Group deleted", "group_id": group_id}
