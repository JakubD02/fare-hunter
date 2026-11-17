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
        "duration": FlightPrice.duration,
    }

    def cheapest_per_airline(self, route_id: str) -> list[tuple[FlightPrice, int]]:
        ranked = (
            select(
                FlightPrice.id,
                func.row_number()
                .over(
                    partition_by=FlightPrice.airline_id,
                    order_by=(FlightPrice.price.asc(), FlightPrice.fetched_at.desc()),
                )
                .label("rn"),
                func.count().over(partition_by=FlightPrice.airline_id).label("offers"),
            )
            .where(FlightPrice.route_id == route_id)
            .subquery()
        )
        stmt = (
            select(FlightPrice, ranked.c.offers)
            .join(ranked, FlightPrice.id == ranked.c.id)
            .where(ranked.c.rn == 1)
            .order_by(FlightPrice.price.asc())
        )
        return [(row[0], row[1]) for row in self._db.execute(stmt).all()]

    def list_for_route(
        self,
        route_id: str,
        limit: int,
        offset: int,
        round_trip: bool,
        sort_by: HistorySortField = "fetched_at",
        order: SortOrder = "desc",
        layover: bool | None = None,
        airline_id: str | None = None,
    ) -> list[FlightPrice]:
        trip_filter = FlightPrice.return_date.is_not(None) if round_trip else FlightPrice.return_date.is_(None)
        column = self.SORT_COLUMNS[sort_by]
        direction = column.desc() if order == "desc" else column.asc()

        query = select(FlightPrice).where(FlightPrice.route_id == route_id, trip_filter)
        if layover is not None:
            query = query.where(FlightPrice.layover == layover)
        if sort_by == "airline":
            query = query.join(Airline, FlightPrice.airline_id == Airline.id)
        if airline_id is not None:
            query = query.where(FlightPrice.airline_id == airline_id)

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
