from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator

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
    route_id: str
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

    @model_validator(mode="before")
    @classmethod
    def reject_null_values(cls, data):
        if isinstance(data, dict):
            for field, value in data.items():
                if value is None:
                    raise ValueError(f"{field} cannot be null")
        return data


class PriceAlertRead(PriceAlertBase):
    id: str
    route_id: str
    last_notified_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
