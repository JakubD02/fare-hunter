from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.flight_price import FlightPrice


class FlightPriceRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, flight_price: FlightPrice) -> FlightPrice:
        self._db.add(flight_price)
        self._db.commit()
        self._db.refresh(flight_price)
        return flight_price

    def list_for_route(self, route_id: str) -> list[FlightPrice]:
        query = select(FlightPrice).where(FlightPrice.route_id == route_id).order_by(FlightPrice.fetched_at.desc())
        return list(self._db.scalars(query).all())

    def latest_currency(self, route_id: str) -> str | None:
        query = (
            select(FlightPrice.currency)
            .where(FlightPrice.route_id == route_id)
            .order_by(FlightPrice.fetched_at.desc())
            .limit(1)
        )
        return self._db.execute(query).scalar_one_or_none()

    def aggregate_since(self, route_id: str, since: datetime) -> list[dict]:
        query = (
            select(
                FlightPrice.currency.label("currency"),
                func.min(FlightPrice.price).label("min_price"),
                func.max(FlightPrice.price).label("max_price"),
                func.avg(FlightPrice.price).label("avg_price"),
                func.count(FlightPrice.price).label("sample_count"),
            )
            .where(
                FlightPrice.route_id == route_id,
                FlightPrice.fetched_at >= since,
            )
            .group_by(FlightPrice.currency)
            .order_by(FlightPrice.currency)
        )
        return [dict(row._mapping) for row in self._db.execute(query)]
