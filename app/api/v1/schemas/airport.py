from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.config import settings


class AirportBase(BaseModel):
    iata_code: str = Field(min_length=settings.airports.iata_code_length, max_length=settings.airports.iata_code_length)
    name: str = Field(min_length=settings.airports.name_min_length, max_length=settings.airports.name_max_length)
    city: str = Field(min_length=settings.airports.city_min_length, max_length=settings.airports.city_max_length)
    country: str = Field(
        min_length=settings.airports.country_min_length, max_length=settings.airports.country_max_length
    )
    country_code: str = Field(
        min_length=settings.airports.country_code_length, max_length=settings.airports.country_code_length
    )

    @field_validator("iata_code", "country_code")
    @classmethod
    def normalize_codes(cls, v: str) -> str:
        return v.strip().upper()

    @field_validator("name", "city", "country")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class AirportCreate(AirportBase):
    pass


class AirportUpdate(BaseModel):
    iata_code: str | None = Field(
        default=None, min_length=settings.airports.iata_code_length, max_length=settings.airports.iata_code_length
    )
    name: str | None = Field(
        default=None, min_length=settings.airports.name_min_length, max_length=settings.airports.name_max_length
    )
    city: str | None = Field(
        default=None, min_length=settings.airports.city_min_length, max_length=settings.airports.city_max_length
    )
    country: str | None = Field(
        default=None, min_length=settings.airports.country_min_length, max_length=settings.airports.country_max_length
    )
    country_code: str | None = Field(
        default=None, min_length=settings.airports.country_code_length, max_length=settings.airports.country_code_length
    )

    @field_validator("iata_code", "country_code")
    @classmethod
    def normalize_codes(cls, v: str | None) -> str | None:
        return v.strip().upper() if v is not None else None

    @field_validator("name", "city", "country")
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


class AirportRead(AirportBase):
    id: str

    model_config = ConfigDict(from_attributes=True)
