from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import (
    ForeignKey,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.price import (
    PRICE_DECIMAL_PLACES,
    PRICE_MAX_DIGITS,
)
from app.enums.currency import Currency
from app.models.base import Base, generate_uuid_string


class FlightPrice(Base):
    __tablename__ = "flight_prices"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid_string)
    route_id: Mapped[str] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=False, index=True)
    airline_id: Mapped[str] = mapped_column(ForeignKey("airlines.id"), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(PRICE_MAX_DIGITS, PRICE_DECIMAL_PLACES), nullable=False)
    currency: Mapped[Currency] = mapped_column(SqlEnum(Currency), default=Currency.PLN, nullable=False)
    departure_date: Mapped[date] = mapped_column(nullable=False)
    return_date: Mapped[date | None] = mapped_column()
    fetched_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False, index=True)
