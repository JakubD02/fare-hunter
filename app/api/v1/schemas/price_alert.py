from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.api.v1.schemas.base import UpdateSchemaBase
from app.api.v1.schemas.types import Price


class PriceAlertBase(BaseModel):
    threshold_price: Price
    is_active: bool = True


class PriceAlertCreate(PriceAlertBase):
    route_id: str


class PriceAlertUpdate(UpdateSchemaBase):
    threshold_price: Price | None = None
    is_active: bool | None = None


class PriceAlertRead(PriceAlertBase):
    id: str
    route_id: str
    last_notified_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
