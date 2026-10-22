from pydantic import BaseModel, ConfigDict

from app.api.v1.schemas.base import UpdateSchemaBase
from app.api.v1.schemas.types import AirportIataCode, AirportName, CityName, Country, CountryCode


class AirportBase(BaseModel):
    iata_code: AirportIataCode
    name: AirportName
    city: CityName
    country: Country
    country_code: CountryCode


class AirportCreate(AirportBase):
    pass


class AirportUpdate(UpdateSchemaBase):
    iata_code: AirportIataCode | None = None
    name: AirportName | None = None
    city: CityName | None = None
    country: Country | None = None
    country_code: CountryCode | None = None


class AirportRead(AirportBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
