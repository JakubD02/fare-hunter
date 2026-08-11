
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.airport import (
    CITY_MAX_LENGTH,
    CITY_MIN_LENGTH,
    COUNTRY_CODE_LENGTH,
    COUNTRY_MAX_LENGTH,
    COUNTRY_MIN_LENGTH,
    IATA_CODE_LENGTH,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
)


class AirportBase(BaseModel):
    iata_code: str = Field(min_length=IATA_CODE_LENGTH, max_length=IATA_CODE_LENGTH)
    name: str = Field(min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)
    city: str = Field(min_length=CITY_MIN_LENGTH, max_length=CITY_MAX_LENGTH)
    country: str = Field(min_length=COUNTRY_MIN_LENGTH, max_length=COUNTRY_MAX_LENGTH)
    country_code: str = Field(
        min_length=COUNTRY_CODE_LENGTH, max_length=COUNTRY_CODE_LENGTH
    )

    @field_validator("iata_code", "country_code")
    @classmethod
    def uppercase_codes(cls, v: str) -> str:
        return v.upper()


class AirportCreate(AirportBase):
    pass


class AirportUpdate(BaseModel):
    iata_code: str | None = Field(
        default=None, min_length=IATA_CODE_LENGTH, max_length=IATA_CODE_LENGTH
    )
    name: str | None = Field(
        default=None, min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH
    )
    city: str | None = Field(
        default=None, min_length=CITY_MIN_LENGTH, max_length=CITY_MAX_LENGTH
    )
    country: str | None = Field(
        default=None, min_length=COUNTRY_MIN_LENGTH, max_length=COUNTRY_MAX_LENGTH
    )
    country_code: str | None = Field(
        default=None, min_length=COUNTRY_CODE_LENGTH, max_length=COUNTRY_CODE_LENGTH
    )

    @field_validator("iata_code", "country_code")
    @classmethod
    def uppercase_codes(cls, v: str) -> str | None:
        return v.upper()


class AirportRead(AirportBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
