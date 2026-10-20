from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.config import settings
from app.enums.currency import Currency


class FlightPriceBase(BaseModel):
    price: Decimal = Field(
        ge=settings.price.price_min_value,
        max_digits=settings.price.price_max_digits,
        decimal_places=settings.price.price_decimal_places,
    )
    currency: Currency = Currency.PLN
    departure_date: date
    return_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.return_date is not None and self.return_date < self.departure_date:
            raise ValueError("return_date cannot precede departure_date")
        return self


class FlightStats(BaseModel):
    route_id: str
    period_days: int = Field(gt=0)
    sample_count: int = Field(ge=0)
    currency: Currency | None
    min_price: Decimal | None
    max_price: Decimal | None
    avg_price: Decimal | None


class FlightPriceRead(FlightPriceBase):
    id: str
    route_id: str
    airline_id: str
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)
