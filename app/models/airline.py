from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.models.base import IdModel


class Airline(IdModel):
    __tablename__ = "airlines"

    iata_code: Mapped[str] = mapped_column(
        String(settings.airline.iata_code_length), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(settings.airline.name_max_length), nullable=False)
