from datetime import date

from pydantic import BaseModel, ConfigDict


class FeaturedRouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    origin_id: str
    destination_id: str
    departure_date: date
    return_date: date | None
    currency: str
