from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.constants.price import MIN_PRICE_VALUE, MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS
from app.enums.currency import Currency


class FlightPrice(BaseModel):
    price: Decimal = Field(
        ge=MIN_PRICE_VALUE,
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
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
