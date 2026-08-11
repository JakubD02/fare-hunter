from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import (
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.price import (
    MONEY_DECIMAL_PLACES,
    MONEY_MAX_DIGITS,
)
from app.enums.currency import Currency
from app.models.base import Base


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(
        ForeignKey("routes.id"), unique=True, nullable=False
    )
    threshold_price: Mapped[Decimal] = mapped_column(
        Numeric(MONEY_MAX_DIGITS, MONEY_DECIMAL_PLACES), nullable=False
    )
    currency: Mapped[Currency] = mapped_column(
        SqlEnum(Currency), default=Currency.PLN, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_notified_at: Mapped[datetime | None] = mapped_column()
