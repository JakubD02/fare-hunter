
from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, Numeric, String

from app.models.base import Base


class FlightPrice(Base):
    __tablename__ = "flights_price"

    id = Column(BigInteger, primary_key=True, index=True)
    route_id = Column(Integer, ForeignKey("routes.id"), nullable=False, index=True)
    airline_id = Column(Integer, ForeignKey("airlines.id"), nullable=False, index=True)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="PLN")
    departue_date = Column(Date(), nullable=False)
    return_date = Column(Date(), nullable=True)
    fetched_at = Column(DateTime(), nullable=False, index=True)