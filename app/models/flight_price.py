from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import (
    ForeignKey,
    Numeric,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.price import (
    PRICE_DECIMAL_PLACES,
    PRICE_MAX_DIGITS,
)
from app.enums.currency import Currency
from app.models.base import Base


class FlightPrice(Base):
    __tablename__ = "flight_prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False)
    airline_id: Mapped[int] = mapped_column(ForeignKey("airlines.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(
        Numeric(PRICE_MAX_DIGITS, PRICE_DECIMAL_PLACES), nullable=False
    )
    currency: Mapped[Currency] = mapped_column(
        SqlEnum(Currency), default=Currency.PLN, nullable=False
    )
    departure_date: Mapped[date] = mapped_column(nullable=False)
    return_date: Mapped[date | None] = mapped_column()
    fetched_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, index=True
    )
