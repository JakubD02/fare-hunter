# app/schemas/airline.py
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

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
    def normalize_iata_code(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("name")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class AirlineCreate(AirlineBase):
    pass


class AirlineUpdate(BaseModel):
    iata_code: str | None = Field(default=None, min_length=IATA_CODE_LENGTH, max_length=IATA_CODE_LENGTH)
    name: str | None = Field(default=None, min_length=NAME_MIN_LENGTH, max_length=NAME_MAX_LENGTH)

    @field_validator("iata_code")
    @classmethod
    def uppercase_code(cls, v: str | None) -> str | None:
        return v.strip().upper() if v is not None else None

    @field_validator("name")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if value is not None else None

    @model_validator(mode="before")
    @classmethod
    def reject_null_values(cls, data):
        if isinstance(data, dict):
            for field, value in data.items():
                if value is None:
                    raise ValueError(f"{field} cannot be null")
        return data


class AirlineRead(AirlineBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
