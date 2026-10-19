from jwt import InvalidTokenError as JWTError

from app.core.security import create_access_token, decode_refresh_token, verify_password
from app.models.user import User
from app.services.user_service import UserService


class AuthService:
    def __init__(self, users: UserService) -> None:
        self._users = users

    def authenticate(self, email: str, password: str) -> User | None:
        user = self._users.get_by_email(email)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    def get_active_user(self, user_id: str) -> User | None:
        user = self._users.get_by_id(user_id)
        if user is None or not user.is_active:
            return None
        return user

    def refresh_access_token(self, refresh_token: str) -> str | None:
        try:
            decoded = decode_refresh_token(refresh_token)
        except JWTError:
            return None

        user_id = decoded.get("user_id")
        if not user_id:
            return None

        user = self.get_active_user(user_id)
        if user is None:
            return None
        return create_access_token(email=user.email, user_id=str(user.id))
