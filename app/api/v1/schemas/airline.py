from pydantic import BaseModel, ConfigDict

from app.api.v1.schemas.base import UpdateSchemaBase
from app.api.v1.schemas.types import AirlineIataCode, AirlineName


class AirlineBase(BaseModel):
    iata_code: AirlineIataCode
    name: AirlineName


class AirlineCreate(AirlineBase):
    pass


class AirlineUpdate(UpdateSchemaBase):
    iata_code: AirlineIataCode | None = None
    name: AirlineName | None = None


class AirlineRead(AirlineBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
