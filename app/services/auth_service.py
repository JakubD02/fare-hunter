import logging

from jwt import InvalidTokenError as JWTError

from app.core.security import create_access_token, decode_refresh_token, verify_password
from app.models.user import User
from app.services.user_service import UserService

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, users: UserService) -> None:
        self._users = users

    def authenticate(self, email: str, password: str) -> User | None:
        user = self._users.get_by_email(email)
        if user is None:
            logger.warning("login failed: unknown account")
            return None
        if not user.is_active:
            logger.warning("login failed: inactive account user_id=%s", user.id)
            return None
        if not verify_password(password, user.password_hash):
            logger.warning("login failed: wrong password user_id=%s", user.id)
            return None

        logger.info("login ok user_id=%s", user.id)
        return user

    def get_active_user(self, user_id: str) -> User | None:
        user = self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            logger.warning("token user rejected user_id=%s", user_id)
            return None
        return user

    def refresh_access_token(self, refresh_token: str) -> str | None:
        try:
            decoded = decode_refresh_token(refresh_token)
        except JWTError as exc:
            logger.warning("refresh rejected: invalid token reason=%s", exc)
            return None

        user_id = decoded.get("user_id")
        if not user_id:
            logger.warning("refresh rejected: token without user_id")
            return None

        user = self.get_active_user(user_id)
        if user is None:
            return None
        logger.info("access token refreshed user_id=%s", user.id)
        return create_access_token(email=user.email, user_id=str(user.id))
