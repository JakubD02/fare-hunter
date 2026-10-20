from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.models.base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(settings.user_config.first_name_max_length), nullable=False)
    email: Mapped[str] = mapped_column(
        String(settings.user_config.email_max_length), nullable=False, index=True, unique=True
    )
    password_hash: Mapped[str] = mapped_column(String(settings.user_config.password_hash_max_length), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
