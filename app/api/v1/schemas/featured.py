from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FeaturedRouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    origin_id: str
    destination_id: str
    departure_date: date
    return_date: date | None
    currency: str


class AirlineCheapestRead(BaseModel):
    airline_id: str
    price: Decimal
    currency: str
    departure_date: date
    fetched_at: datetime
    offers_count: int
