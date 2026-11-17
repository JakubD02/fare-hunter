
from fastapi import APIRouter, HTTPException, Query
from starlette import status

from app.api.auth import CurrentUser
from app.api.v1.dependencies import FlightPriceServiceDep, PaginationDep
from app.api.v1.schemas.featured import AirlineCheapestRead
from app.api.v1.schemas.flight_price import FlightPriceRead, FlightStats
from app.enums.sorting import HistorySortField, SortOrder

router = APIRouter(prefix="/routes", tags=["statistics"])


@router.get("/{route_id}/stats", response_model=FlightStats)
def get_stats(route_id: str, service: FlightPriceServiceDep, user: CurrentUser) -> FlightStats:
    stats = service.get_stats(user, route_id)
    if stats is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return FlightStats.model_validate(stats)


@router.get("/{route_id}/history", response_model=list[FlightPriceRead])
def get_history(
    route_id: str,
    service: FlightPriceServiceDep,
    user: CurrentUser,
    *,
    pagination: PaginationDep,
    sort_by: HistorySortField = "fetched_at",
    order: SortOrder = "desc",
    layover: bool | None = Query(default=None),
    airline_id: str | None = Query(default=None),
) -> list[FlightPriceRead]:
    history = service.get_history(
        user,
        route_id,
        limit=pagination.limit,
        offset=pagination.offset,
        sort_by=sort_by,
        order=order,
        layover=layover,
        airline_id=airline_id,
    )
    if history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return [FlightPriceRead.model_validate(item) for item in history]

@router.get("/{route_id}/airlines", response_model=list[AirlineCheapestRead])
def get_cheapest_per_airline(
    route_id: str,
    user: CurrentUser,
    prices: FlightPriceServiceDep,
) -> list[AirlineCheapestRead]:
    rows = prices.get_cheapest_per_airline(user, route_id)
    if rows is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return [
        AirlineCheapestRead(
            airline_id=price.airline_id,
            price=price.price,
            currency=price.currency,
            departure_date=price.departure_date,
            fetched_at=price.fetched_at,
            offers_count=count,
        )
        for price, count in rows
    ]
