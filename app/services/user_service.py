from app.api.v1.schemas.user import UserCreate
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def get_by_id(self, user_id: str) -> User | None:
        return self._users.get_by_id(user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._users.get_by_email(email)

    def register(self, user_in: UserCreate) -> User | None:
        user = User(
            first_name=user_in.first_name,
            email=user_in.email,
            password_hash=hash_password(user_in.password),
        )
        return self._users.add(user)
