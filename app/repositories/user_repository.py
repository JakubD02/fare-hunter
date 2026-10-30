from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        return self._db.execute(select(User).where(func.lower(User.email) == email.lower())).scalar_one_or_none()

    def try_add(self, user: User) -> User | None:
        """Add a user - return None if the email is already taken."""
        try:
            return self.add(user)
        except IntegrityError:
            self._db.rollback()
            return None
