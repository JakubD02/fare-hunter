from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.airport import (
    CITY_MAX_LENGTH,
    COUNTRY_CODE_LENGTH,
    COUNTRY_MAX_LENGTH,
    IATA_CODE_LENGTH,
    NAME_MAX_LENGTH,
)
from app.models.base import IdModel


class Airport(IdModel):
    __tablename__ = "airports"

    iata_code: Mapped[str] = mapped_column(String(IATA_CODE_LENGTH), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False, unique=True)
    city: Mapped[str] = mapped_column(String(CITY_MAX_LENGTH), nullable=False)
    country: Mapped[str] = mapped_column(String(COUNTRY_MAX_LENGTH), nullable=False)
    country_code: Mapped[str] = mapped_column(String(COUNTRY_CODE_LENGTH), nullable=False, index=True)
