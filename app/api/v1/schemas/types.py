from decimal import Decimal
from typing import Annotated

from fastapi import Query
from pydantic import AfterValidator, EmailStr, Field, StringConstraints

from app.core.config import settings

# --- Price ---

Price = Annotated[
    Decimal,
    Field(
        ge=settings.price.price_min_value,
        max_digits=settings.price.price_max_digits,
        decimal_places=settings.price.price_decimal_places,
    ),
]

# --- Airports ---

AirportIataCode = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_upper=True,
        min_length=settings.airports.iata_code_length,
        max_length=settings.airports.iata_code_length,
    ),
]

AirportName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=settings.airports.name_min_length,
        max_length=settings.airports.name_max_length,
    ),
]

CityName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=settings.airports.city_min_length,
        max_length=settings.airports.city_max_length,
    ),
]

Country = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=settings.airports.country_min_length,
        max_length=settings.airports.country_max_length,
    ),
]

CountryCode = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_upper=True,
        min_length=settings.airports.country_code_length,
        max_length=settings.airports.country_code_length,
    ),
]

# --- Airlines ---

AirlineIataCode = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        to_upper=True,
        min_length=settings.airline.iata_code_length,
        max_length=settings.airline.iata_code_length,
    ),
]

AirlineName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=settings.airline.name_min_length,
        max_length=settings.airline.name_max_length,
    ),
]

# --- User ---

FirstName = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=settings.user_config.first_name_min_length,
        max_length=settings.user_config.first_name_max_length,
    ),
]


def _normalize_email(value: str) -> str:
    return value.lower()


Email = Annotated[
    EmailStr,
    AfterValidator(_normalize_email),
    Field(max_length=settings.user_config.email_max_length),
]

Password = Annotated[
    str,
    StringConstraints(
        min_length=settings.user_config.password_min_length,
        max_length=settings.user_config.password_max_length,
    ),
]

# --- Pagination ---

Limit = Annotated[
    int,
    Query(ge=settings.pagination.min_limit, le=settings.pagination.max_limit),
]

Offset = Annotated[
    int,
    Query(ge=settings.pagination.min_offset),
]
