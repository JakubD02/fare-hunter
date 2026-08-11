from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.constants.price import MIN_PRICE_VALUE, MONEY_DECIMAL_PLACES, MONEY_MAX_DIGITS
from app.enums.currency import Currency


class PriceAlertBase(BaseModel):
    threshold_price: Decimal = Field(
        ge=MIN_PRICE_VALUE,
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
    )
    currency: Currency = Currency.PLN
    is_active: bool = True


class PriceAlertCreate(PriceAlertBase):
    pass


class PriceAlertUpdate(BaseModel):
    threshold_price: Decimal | None = Field(
        default=None,
        ge=MIN_PRICE_VALUE,
        max_digits=MONEY_MAX_DIGITS,
        decimal_places=MONEY_DECIMAL_PLACES,
    )
    currency: Currency | None = None
    is_active: bool | None = None


class PriceAlertRead(PriceAlertBase):
    id: int
    route_id: int
    last_notified_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
