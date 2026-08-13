from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.constants.price import PRICE_DECIMAL_PLACES, PRICE_MAX_DIGITS, PRICE_MIN_VALUE
from app.enums.currency import Currency


class FlightPrice(BaseModel):
    price: Decimal = Field(
        ge=PRICE_MIN_VALUE,
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
    )
    currency: Currency = Currency.PLN
    departure_date: date
    return_date: date | None = None


class FlightPriceRead(FlightPrice):
    id: int
    route_id: int
    air_line_id: int
    fetched_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
