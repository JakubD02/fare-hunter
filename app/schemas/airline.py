# app/schemas/airline.py
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.airline import (
    IATA_CODE_LENGTH,
    NAME_MAX_LENGTH,
    NAME_MIN_LENGTH,
)


class AirlineBase(BaseModel):
    iata_code: str = Field(min_length=IATA_CODE_LENGTH, max_length=IATA_CODE_LENGTH)
    name: str = Field(min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)

    @field_validator("iata_code")
    @classmethod
    def uppercase_code(cls, v: str) -> str:
        return v.upper()


class AirlineCreate(AirlineBase):
    pass


class AirlineUpdate(BaseModel):
    iata_code: str | None = Field(
        default=None, min_length=IATA_CODE_LENGTH, max_length=IATA_CODE_LENGTH
    )
    name: str | None = Field(
        default=None, min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH
    )

    @field_validator("iata_code")
    @classmethod
    def uppercase_code(cls, v: str | None) -> str | None:
        return v.upper() if v else v


class AirlineRead(AirlineBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
