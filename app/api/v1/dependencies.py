from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.services.alert_service import AlertService
from app.services.auth_service import AuthService
from app.services.factories import (
    build_alert_service,
    build_auth_service,
    build_flight_price_service,
    build_reference_service,
    build_route_service,
    build_user_service,
)
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
    return build_user_service(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


def get_auth_service(db: DbSession) -> AuthService:
    return build_auth_service(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_route_service(db: DbSession) -> RouteService:
    return build_route_service(db)


RouteServiceDep = Annotated[RouteService, Depends(get_route_service)]


def get_alert_service(db: DbSession) -> AlertService:
    return build_alert_service(db)


AlertServiceDep = Annotated[AlertService, Depends(get_alert_service)]


def get_flight_price_service(db: DbSession) -> FlightPriceService:
    return build_flight_price_service(db)


FlightPriceServiceDep = Annotated[FlightPriceService, Depends(get_flight_price_service)]


def get_reference_service(db: DbSession) -> ReferenceService:
    return build_reference_service(db)


ReferenceServiceDep = Annotated[ReferenceService, Depends(get_reference_service)]
