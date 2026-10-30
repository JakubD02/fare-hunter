from datetime import date

from sqlalchemy import Enum as StrEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums.currency import Currency
from app.models.airport import Airport
from app.models.base import BaseModel


class Route(BaseModel):
    __tablename__ = "routes"

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    currency: Mapped[Currency] = mapped_column(
        StrEnum(Currency, native_enum=False),
        default=Currency.PLN,
        server_default=Currency.PLN.value,
        nullable=False,
    )
    origin_id: Mapped[str] = mapped_column(ForeignKey("airports.id"), nullable=False, index=True)
    destination_id: Mapped[str] = mapped_column(ForeignKey("airports.id"), nullable=False, index=True)
    departure_date: Mapped[date] = mapped_column(nullable=False)
    return_date: Mapped[date | None] = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    origin_airport: Mapped["Airport"] = relationship(foreign_keys=[origin_id])
    destination_airport: Mapped["Airport"] = relationship(foreign_keys=[destination_id])

    __table_args__ = (
        UniqueConstraint("user_id", "origin_id", "destination_id", name="uq_route_user_origin_destination"),
    )
