
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric, String

from app.enums.currency import Currency
from app.models.base import Base


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(BigInteger, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("route.id"), index=True)
    threshold_price = Column(Numeric(10, 2))
    currency = Column(Currency, default=Currency.PLN)
    is_active = Column(Boolean, default=True)
    last_notified_at = Column(DateTime, nullable=True)