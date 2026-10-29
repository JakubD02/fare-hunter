from fastapi import APIRouter, HTTPException
from starlette import status

from app.api.auth import CurrentUser
from app.api.v1.dependencies import FlightPriceServiceDep, PaginationDep
from app.api.v1.schemas.flight_price import FlightPriceRead, FlightStats

router = APIRouter(prefix="/routes", tags=["statistics"])


@router.get("/{route_id}/stats", response_model=FlightStats)
def get_stats(route_id: str, service: FlightPriceServiceDep, user: CurrentUser) -> FlightStats:
    stats = service.get_stats(user, route_id)
    if stats is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return FlightStats.model_validate(stats)


@router.get("/{route_id}/history", response_model=list[FlightPriceRead])
def get_history(
    route_id: str, service: FlightPriceServiceDep, user: CurrentUser, page: PaginationDep
) -> list[FlightPriceRead]:
    history = service.get_history(user, route_id, limit=page.limit, offset=page.offset)
    if history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return [FlightPriceRead.model_validate(item) for item in history]
