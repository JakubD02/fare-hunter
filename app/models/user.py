from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.user import (
    EMAIL_MAX_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH,
)
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(FIRST_NAME_MAX_LENGTH), nullable=False)
    email: Mapped[str] = mapped_column(String(EMAIL_MAX_LENGTH), nullable=False, index=True, unique=True)
    password_hash: Mapped[str] = mapped_column(String(PASSWORD_HASH_MAX_LENGTH), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
