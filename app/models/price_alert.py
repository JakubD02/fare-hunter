
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
)

from app.enums.currency import Currency
from app.models.base import Base
from sqlalchemy import Enum as SqlEnum


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(BigInteger, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), index=True)
    threshold_price = Column(Numeric(10, 2))
    currency = Column(SqlEnum(Currency), default=Currency.PLN)
    is_active = Column(Boolean, default=True)
    last_notified_at = Column(DateTime, nullable=True)
