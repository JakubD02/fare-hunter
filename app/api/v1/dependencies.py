from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.repositories.airline_repository import AirlineRepository
from app.repositories.airport_repository import AirportRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.flight_price_repository import FlightPriceRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.user_repository import UserRepository
from app.services.alert_service import AlertService
from app.services.auth_service import AuthService
from app.services.flight_price_service import FlightPriceService
from app.services.reference_service import ReferenceService
from app.services.route_service import RouteService
from app.services.user_service import UserService

# --- session ---
DbSession = Annotated[Session, Depends(get_db)]


# --- pagination ---
@dataclass(frozen=True)
class Pagination:
    limit: int
    offset: int


def get_pagination(
    limit: int = Query(
        default=settings.pagination.default_limit,
        ge=settings.pagination.min_limit,
        le=settings.pagination.max_limit,
    ),
    offset: int = Query(default=settings.pagination.default_offset, ge=settings.pagination.min_offset),
) -> Pagination:
    return Pagination(limit=limit, offset=offset)


PaginationDep = Annotated[Pagination, Depends(get_pagination)]


# --- services ---
def get_user_service(db: DbSession) -> UserService:
    return UserService(users=UserRepository(db))


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_auth_service(users: UserServiceDep) -> AuthService:
    return AuthService(users=users)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_route_service(db: DbSession) -> RouteService:
    return RouteService(routes=RouteRepository(db), airports=AirportRepository(db))


RouteServiceDep = Annotated[RouteService, Depends(get_route_service)]


def get_alert_service(db: DbSession, routes: RouteServiceDep) -> AlertService:
    return AlertService(alerts=AlertRepository(db), routes=routes)


AlertServiceDep = Annotated[AlertService, Depends(get_alert_service)]


def get_flight_price_service(db: DbSession, routes: RouteServiceDep) -> FlightPriceService:
    return FlightPriceService(prices=FlightPriceRepository(db), airlines=AirlineRepository(db), routes=routes)


FlightPriceServiceDep = Annotated[FlightPriceService, Depends(get_flight_price_service)]


def get_reference_service(db: DbSession) -> ReferenceService:
    return ReferenceService(airports=AirportRepository(db), airlines=AirlineRepository(db))


ReferenceServiceDep = Annotated[ReferenceService, Depends(get_reference_service)]
