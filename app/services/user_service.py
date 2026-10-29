import logging

from app.api.v1.schemas.user import UserCreate
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def get_by_id(self, user_id: str) -> User | None:
        user = self._users.get_by_id(user_id)
        logger.debug("user lookup by id user_id=%s found=%s", user_id, user is not None)
        return user

    def get_by_email(self, email: str) -> User | None:
        user = self._users.get_by_email(email)
        logger.debug("user lookup by email found=%s", user is not None)
        return user

    def register(self, user_in: UserCreate) -> User | None:
        user = User(
            first_name=user_in.first_name,
            email=user_in.email,
            password_hash=hash_password(user_in.password),
        )
        saved = self._users.try_add(user)
        if saved is None:
            logger.warning("registration rejected: email already in use")
            return None

        logger.info("user registered user_id=%s", saved.id)
        return saved
