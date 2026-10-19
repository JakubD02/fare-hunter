from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self._db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, user_id: str) -> User | None:
        return self._db.get(User, user_id)

    def add(self, user: User) -> User | None:
        self._db.add(user)
        try:
            self._db.commit()
        except IntegrityError:
            self._db.rollback()
            return None

        self._db.refresh(user)
        return user
