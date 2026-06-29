from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User, EmailVerification, PasswordReset
from app.repositories.base import BaseRepository
from typing import Optional


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        query = select(self.model).where(self.model.email == email)
        return self.db.execute(query).scalar_one_or_none()

    def get_by_google_id(self, google_id: str) -> Optional[User]:
        query = select(self.model).where(self.model.google_id == google_id)
        return self.db.execute(query).scalar_one_or_none()


class EmailVerificationRepository(BaseRepository[EmailVerification]):
    def __init__(self, db: Session):
        super().__init__(EmailVerification, db)

    def get_by_token(self, token: str) -> Optional[EmailVerification]:
        query = select(self.model).where(self.model.token == token)
        return self.db.execute(query).scalar_one_or_none()


class PasswordResetRepository(BaseRepository[PasswordReset]):
    def __init__(self, db: Session):
        super().__init__(PasswordReset, db)

    def get_by_token(self, token: str) -> Optional[PasswordReset]:
        query = select(self.model).where(self.model.token == token)
        return self.db.execute(query).scalar_one_or_none()
