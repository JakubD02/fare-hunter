from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class RouteBase(BaseModel):
    origin_id: str
    destination_id: str
    departure_date: date
    return_date: date | None = None
    is_active: bool = True


class RouteCreate(RouteBase):
    pass


class RouteUpdate(BaseModel):
    origin_id: str | None = None
    destination_id: str | None = None
    departure_date: date | None = None
    return_date: date | None = None
    is_active: bool | None = None


class RouteRead(RouteBase):
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
