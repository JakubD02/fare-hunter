from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, ValidationInfo, field_validator


def validate_departure_date(val: date) -> date:
    if val <= date.today():
        raise ValueError("Departure_date must be in the future")
    return val


def validate_return_date(value: date | None, departure: date | None) -> date | None:
    if value is not None and departure is not None and value < departure:
        raise ValueError("Return date must not be before departure date")
    return value


class RouteFields(BaseModel):
    origin_id: str
    destination_id: str
    departure_date: date
    return_date: date | None = None
    is_active: bool = True


class RouteCreate(RouteFields):
    @field_validator("departure_date")
    @classmethod
    def departure_date_must_be_in_future(cls, value: date) -> date:
        return validate_departure_date(value)

    @field_validator("return_date")
    @classmethod
    def return_date_must_follow_departure(cls, value: date | None, info: ValidationInfo) -> date | None:
        return validate_return_date(value, info.data.get("departure_date"))

    @field_validator("destination_id")
    @classmethod
    def destination_must_differ_from_origin(cls, value: str, info: ValidationInfo) -> str:
        origin = info.data.get("origin_id")
        if origin is not None and value == origin:
            raise ValueError("Origin and destination must be different")
        return value


class RouteUpdate(BaseModel):
    origin_id: str | None = None
    destination_id: str | None = None
    departure_date: date | None = None
    return_date: date | None = None
    is_active: bool | None = None

    @field_validator("departure_date")
    @classmethod
    def departure_date_must_be_in_future(cls, value: date | None) -> date | None:
        if value is None:
            raise ValueError("Departure date cannot be null")
        return validate_departure_date(value)


class RouteRead(RouteFields):
    id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
