from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.api.v1.schemas.base import UpdateSchemaBase
from app.api.v1.schemas.types import Email, FirstName, Password


class UserBase(BaseModel):
    first_name: FirstName
    email: Email


class UserCreate(UserBase):
    password: Password


class UserUpdate(UpdateSchemaBase):
    first_name: FirstName | None = None
    email: Email | None = None


class UserRead(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
