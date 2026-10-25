from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import (
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.config import settings
from app.enums.currency import Currency
from app.models.base import BaseModel


class PriceAlert(BaseModel):
    __tablename__ = "price_alerts"

    route_id: Mapped[str] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), unique=True, nullable=False)
    threshold_price: Mapped[Decimal] = mapped_column(
        Numeric(settings.price.price_max_digits, settings.price.price_decimal_places), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    last_notified_at: Mapped[datetime | None] = mapped_column()
