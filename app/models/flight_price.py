from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import (
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.enums.currency import Currency
from app.models.base import IdModel


class FlightPrice(IdModel):
    __tablename__ = "flight_prices"

    route_id: Mapped[str] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=False, index=True)
    airline_id: Mapped[str] = mapped_column(ForeignKey("airlines.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(
        Numeric(settings.price.price_max_digits, settings.price.price_decimal_places), nullable=False
    )
    currency: Mapped[Currency] = mapped_column(SqlEnum(Currency), nullable=False)
    departure_date: Mapped[date] = mapped_column(nullable=False)
    return_date: Mapped[date | None] = mapped_column()
    fetched_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False, index=True)
