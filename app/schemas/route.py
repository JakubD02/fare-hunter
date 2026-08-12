from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RouteBase(BaseModel):
    origin_id: int
    destination_id: int
    departure_date: date
    return_date: date | None = None
    is_active: bool = True


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    origin_id: int | None = None
    destination_id: int | None = None
    departure_date: date | None = None
    return_date: date | None = None
    is_active: bool | None = None


class RouteRead(RouteBase):
    id: int
    user_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
