from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.models.base import IdModel


class Airport(IdModel):
    __tablename__ = "airports"

    iata_code: Mapped[str] = mapped_column(
        String(settings.airports.iata_code_length), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(settings.airports.name_max_length), nullable=False, unique=True)
    city: Mapped[str] = mapped_column(String(settings.airports.city_max_length), nullable=False)
    country: Mapped[str] = mapped_column(String(settings.airports.country_max_length), nullable=False)
    country_code: Mapped[str] = mapped_column(String(settings.airports.country_code_length), nullable=False, index=True)
