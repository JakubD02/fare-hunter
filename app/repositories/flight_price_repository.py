from datetime import datetime
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import func, select

from app.enums.currency import Currency
from app.models.flight_price import FlightPrice
from app.repositories.base_repository import BaseRepository


class PriceAggregate(TypedDict):
    currency: Currency
    min_price: Decimal
    max_price: Decimal
    avg_price: Decimal
    sample_count: int


class FlightPriceRepository(BaseRepository[FlightPrice]):
    model = FlightPrice

    def list_for_route(self, route_id: str, limit: int, offset: int) -> list[FlightPrice]:
        query = (
            select(FlightPrice)
            .where(FlightPrice.route_id == route_id)
            .order_by(FlightPrice.fetched_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self._db.scalars(query).all())

    def aggregate_since(self, route_id: str, since: datetime) -> list[PriceAggregate]:
        query = (
            select(
                FlightPrice.currency,
                func.min(FlightPrice.price).label("min_price"),
                func.max(FlightPrice.price).label("max_price"),
                func.avg(FlightPrice.price).label("avg_price"),
                func.count().label("sample_count"),
            )
            .where(
                FlightPrice.route_id == route_id,
                FlightPrice.fetched_at >= since,
            )
            .group_by(FlightPrice.currency)
            .order_by(FlightPrice.currency)
        )
        return [
            PriceAggregate(
                currency=row.currency,
                min_price=row.min_price,
                max_price=row.max_price,
                avg_price=row.avg_price,
                sample_count=row.sample_count,
            )
            for row in self._db.execute(query)
        ]
