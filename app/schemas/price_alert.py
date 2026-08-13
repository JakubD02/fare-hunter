from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.constants.price import (
    PRICE_DECIMAL_PLACES,
    PRICE_MAX_DIGITS,
    PRICE_MIN_VALUE,
)
from app.enums.currency import Currency


class PriceAlertBase(BaseModel):
    threshold_price: Decimal = Field(
        ge=PRICE_MIN_VALUE,
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
    )
    currency: Currency = Currency.PLN
    is_active: bool = True


class PriceAlertCreate(PriceAlertBase):
    pass


class PriceAlertUpdate(BaseModel):
    threshold_price: Decimal | None = Field(
        default=None,
        ge=PRICE_MIN_VALUE,
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
    )
    currency: Currency | None = None
    is_active: bool | None = None


class PriceAlertRead(PriceAlertBase):
    id: int
    route_id: int
    last_notified_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
