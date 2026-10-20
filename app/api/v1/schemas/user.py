from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.config import settings


class UserBase(BaseModel):
    first_name: str = Field(
        min_length=settings.user_config.first_name_min_length, max_length=settings.user_config.first_name_max_length
    )
    email: EmailStr = Field(max_length=settings.user_config.email_max_length)


class UserCreate(UserBase):
    password: str = Field(
        min_length=settings.user_config.password_min_length, max_length=settings.user_config.password_max_length
    )


class UserUpdate(BaseModel):
    first_name: str | None = Field(
        default=None,
        min_length=settings.user_config.first_name_min_length,
        max_length=settings.user_config.first_name_max_length,
    )
    email: EmailStr | None = Field(default=None, max_length=settings.user_config.email_max_length)


class UserRead(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
