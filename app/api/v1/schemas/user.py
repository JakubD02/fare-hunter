from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, field_validator

from app.api.v1.schemas.base import UpdateSchemaBase
from app.api.v1.schemas.types import Email, FirstName, Password
from app.core.config import settings


class UserBase(BaseModel):
    first_name: FirstName
    email: Email


class UserCreate(UserBase):
    password: Password

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        min_len = settings.user_config.password_min_length
        max_len = settings.user_config.password_max_length

        if len(value) < min_len:
            raise ValueError(f"must be at least {min_len} characters")
        if len(value) > max_len:
            raise ValueError(f"must be at most {max_len} characters")
        if not re.search(r"[a-z]", value):
            raise ValueError("must contain a lowercase letter")
        if not re.search(r"[A-Z]", value):
            raise ValueError("must contain an uppercase letter")
        if not re.search(r"\d", value):
            raise ValueError("must contain a digit")
        if not re.search(r"[^\w]|_", value):
            raise ValueError("must contain a special character")
        return value


class UserUpdate(UpdateSchemaBase):
    first_name: FirstName | None = None
    email: Email | None = None


class UserRead(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
