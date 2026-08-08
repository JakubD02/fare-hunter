from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
)
from sqlalchemy import Enum as SqlEnum

from app.enums.currency import Currency
from app.models.base import Base


class FlightPrice(Base):
    __tablename__ = "flight_prices"

    id = Column(BigInteger, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False, index=True)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(SqlEnum(Currency), nullable=False, default=Currency.PLN)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    fetched_at = Column(DateTime, nullable=False, index=True)
