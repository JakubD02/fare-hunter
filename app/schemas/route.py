from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator


class RouteBase(BaseModel):
    origin_id: str
    destination_id: str
    departure_date: date
    return_date: date | None = None
    is_active: bool = True

    @field_validator("departure_date")
    @classmethod
    def departure_date_must_be_in_future(cls, val: date) -> date:
        if val <= date.today():
            raise ValueError("Departure_date must be in the future")
        return val

    @field_validator("return_date")
    @classmethod
    def return_date_validation(cls, val: date | None, info: ValidationInfo) -> date | None:
        if val is None:
            return val

        departure_date = info.data.get("departure_date")
        if departure_date and val < departure_date:
            raise ValueError("Return_date must not be before departure_date")
        return val


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
