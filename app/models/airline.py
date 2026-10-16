from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.airline import IATA_CODE_LENGTH, NAME_MAX_LENGTH
from app.models.base import IdModel


class Airline(IdModel):
    __tablename__ = "airlines"

    iata_code: Mapped[str] = mapped_column(String(IATA_CODE_LENGTH), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False)
