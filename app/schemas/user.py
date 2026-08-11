from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.constants.user import (
    EMAIL_MAX_LENGTH,
    FIRST_NAME_MAX_LENGTH,
    FIRST_NAME_MIN_LENGTH,
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
)


class UserBase(BaseModel):
    first_name: str = Field(
        min_length=FIRST_NAME_MIN_LENGTH, max_length=FIRST_NAME_MAX_LENGTH
    )
    email: EmailStr = Field(max_length=EMAIL_MAX_LENGTH)


class UserCreate(UserBase):
    password: str = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )


class UserUpdate(UserBase):
    first_name: str | None = Field(
        default=None, min_length=FIRST_NAME_MIN_LENGTH, max_length=FIRST_NAME_MAX_LENGTH
    )
    email: EmailStr | None = Field(default=None, max_length=EMAIL_MAX_LENGTH)


class UserRead(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
