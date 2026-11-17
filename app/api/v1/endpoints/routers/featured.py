from fastapi import APIRouter, HTTPException, Query
from starlette import status

from app.api.v1.dependencies import FeaturedRouteServiceDep, FlightPriceServiceDep, PaginationDep
from app.api.v1.schemas.featured import AirlineCheapestRead, FeaturedRouteRead
from app.api.v1.schemas.flight_price import FlightPriceRead, FlightStats
from app.enums.sorting import HistorySortField, SortOrder

router = APIRouter(prefix="/featured/routes", tags=["featured"])


@router.get("/", response_model=list[FeaturedRouteRead])
def list_featured_routes(service: FeaturedRouteServiceDep, page: PaginationDep):
    return service.list_featured(limit=page.limit, offset=page.offset)


@router.get("/{route_id}", response_model=FeaturedRouteRead)
def get_featured_route(service: FeaturedRouteServiceDep, route_id: str):
    route = service.get_featured_route(route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found.")
    return route


@router.get("/{route_id}/stats", response_model=FlightStats)
def get_featured_stats(
    route_id: str,
    routes: FeaturedRouteServiceDep,
    prices: FlightPriceServiceDep,
):
    route = routes.get_featured_route(route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found.")

    stats = prices.get_stats_for_route(route)
    if stats is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No statistics yet.")
    return stats


@router.get("/{route_id}/history", response_model=list[FlightPriceRead])
def get_featured_history(
    route_id: str,
    routes: FeaturedRouteServiceDep,
    prices: FlightPriceServiceDep,
    pagination: PaginationDep,
    sort_by: HistorySortField = "fetched_at",
    order: SortOrder = "desc",
    layover: bool | None = Query(default=None),
    airline_id: str | None = Query(default=None),
):
    route = routes.get_featured_route(route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found.")

    history = prices.get_history_for_route(
        route,
        limit=pagination.limit,
        offset=pagination.offset,
        sort_by=sort_by,
        order=order,
        layover=layover,
        airline_id=airline_id,
    )
    return history


@router.get("/{route_id}/airlines", response_model=list[AirlineCheapestRead])
def cheapest_per_airline(
    route_id: str,
    featured: FeaturedRouteServiceDep,
    prices: FlightPriceServiceDep,
) -> list[AirlineCheapestRead]:
    route = featured.get_featured_route(route_id)
    if route is None:
        raise HTTPException(status_code=404, detail="Route not found")

    return [
        AirlineCheapestRead(
            airline_id=price.airline_id,
            price=price.price,
            currency=price.currency,
            departure_date=price.departure_date,
            fetched_at=price.fetched_at,
            offers_count=count,
        )
        for price, count in prices.get_cheapest_per_airline_for_route(route)
    ]
