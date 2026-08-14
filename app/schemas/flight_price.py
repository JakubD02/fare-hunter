from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.constants.price import PRICE_DECIMAL_PLACES, PRICE_MAX_DIGITS, PRICE_MIN_VALUE
from app.enums.currency import Currency


class FlightPriceBase(BaseModel):
    price: Decimal = Field(
        ge=PRICE_MIN_VALUE,
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
    )
    currency: Currency = Currency.PLN
    departure_date: date
    return_date: date | None = None


class FlightStats(BaseModel):
    route_id: int
    period_days: int
    sample_count: int
    min_price: Decimal | None
    max_price: Decimal | None
    avg_price: Decimal | None


class FlightPriceRead(FlightPriceBase):
    id: int
    route_id: int
    airline_id: int
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)
