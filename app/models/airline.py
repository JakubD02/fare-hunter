from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.airline import IATA_CODE_LENGTH, NAME_MAX_LENGTH
from app.models.base import Base


class Airline(Base):
    __tablename__ = "airlines"

    id: Mapped[int] = mapped_column(primary_key=True)
    iata_code: Mapped[str] = mapped_column(
        String(IATA_CODE_LENGTH), unique=True, nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=False)
