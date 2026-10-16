from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import (
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.constants.price import (
    PRICE_DECIMAL_PLACES,
    PRICE_MAX_DIGITS,
)
from app.enums.currency import Currency
from app.models.base import BaseModel


class PriceAlert(BaseModel):
    __tablename__ = "price_alerts"

    route_id: Mapped[str] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), unique=True, nullable=False)
    threshold_price: Mapped[Decimal] = mapped_column(Numeric(PRICE_MAX_DIGITS, PRICE_DECIMAL_PLACES), nullable=False)
    currency: Mapped[Currency] = mapped_column(SqlEnum(Currency), default=Currency.PLN, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_notified_at: Mapped[datetime | None] = mapped_column()
