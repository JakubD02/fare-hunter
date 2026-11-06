from datetime import datetime
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import func, select

from app.enums.currency import Currency
from app.enums.sorting import HistorySortField, SortOrder
from app.models.airline import Airline
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

    SORT_COLUMNS = {
        "fetched_at": FlightPrice.fetched_at,
        "price": FlightPrice.price,
        "airline": Airline.name,
    }

    def list_for_route(
        self,
        route_id: str,
        limit: int,
        offset: int,
        round_trip: bool,
        sort_by: HistorySortField = "fetched_at",
        order: SortOrder = "desc",
    ) -> list[FlightPrice]:
        trip_filter = FlightPrice.return_date.is_not(None) if round_trip else FlightPrice.return_date.is_(None)
        column = self.SORT_COLUMNS[sort_by]
        direction = column.desc() if order == "desc" else column.asc()

        query = select(FlightPrice).where(FlightPrice.route_id == route_id, trip_filter)
        if sort_by == "airline":
            query = query.join(Airline, FlightPrice.airline_id == Airline.id)

        query = query.order_by(direction.nulls_last(), FlightPrice.id).limit(limit).offset(offset)
        return list(self._db.scalars(query))

    def aggregate_since(self, route_id: str, since: datetime, round_trip: bool) -> list[PriceAggregate]:
        trip_filter = FlightPrice.return_date.is_not(None) if round_trip else FlightPrice.return_date.is_(None)
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
                trip_filter,
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
