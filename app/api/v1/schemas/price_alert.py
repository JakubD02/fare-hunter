from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.api.v1.schemas.base import UpdateSchemaBase
from app.api.v1.schemas.types import Price
from app.enums.currency import Currency


class PriceAlertBase(BaseModel):
    threshold_price: Price
    currency: Currency = Currency.PLN
    is_active: bool = True


class PriceAlertCreate(PriceAlertBase):
    route_id: str
    pass


class PriceAlertUpdate(UpdateSchemaBase):
    threshold_price: Price | None = None
    currency: Currency | None = None
    is_active: bool | None = None


class PriceAlertRead(PriceAlertBase):
    id: str
    route_id: str
    last_notified_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
