from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.api.auth import CurrentUser
from app.api.v1.dependencies import PaginationDep
from app.api.v1.schemas.flight_price import FlightPriceRead, FlightStats
from app.core.database import get_db
from app.repositories.airline_repository import AirlineRepository
from app.repositories.airport_repository import AirportRepository
from app.repositories.flight_price_repository import FlightPriceRepository
from app.repositories.route_repository import RouteRepository
from app.services.flight_price_service import FlightPriceService
from app.services.route_service import RouteService

router = APIRouter(prefix="/routes", tags=["statistics"])

db_dependency = Annotated[Session, Depends(get_db)]


def _flight_price_service(db: Session) -> FlightPriceService:
    return FlightPriceService(
        prices=FlightPriceRepository(db),
        airlines=AirlineRepository(db),
        routes=RouteService(
            routes=RouteRepository(db),
            airports=AirportRepository(db),
        ),
    )


@router.get("/{route_id}/stats", response_model=FlightStats)
def get_stats(route_id: str, db: db_dependency, user: CurrentUser) -> FlightStats:
    stats = _flight_price_service(db).get_stats(user, route_id)
    if stats is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return FlightStats.model_validate(stats)


@router.get("/{route_id}/history", response_model=list[FlightPriceRead])
def get_history(route_id: str, db: db_dependency, user: CurrentUser, page: PaginationDep) -> list[FlightPriceRead]:
    history = _flight_price_service(db).get_history(user, route_id, limit=page.limit, offset=page.offset)
    if history is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return [FlightPriceRead.model_validate(item) for item in history]
