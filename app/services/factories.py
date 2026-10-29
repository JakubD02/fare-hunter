from sqlalchemy.orm import Session

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


def build_user_service(db: Session) -> UserService:
    return UserService(users=UserRepository(db))


def build_auth_service(db: Session) -> AuthService:
    return AuthService(users=build_user_service(db))


def build_route_service(db: Session) -> RouteService:
    return RouteService(routes=RouteRepository(db), airports=AirportRepository(db))


def build_alert_service(db: Session) -> AlertService:
    return AlertService(alerts=AlertRepository(db), routes=build_route_service(db))


def build_flight_price_service(db: Session) -> FlightPriceService:
    return FlightPriceService(
        prices=FlightPriceRepository(db),
        airlines=AirlineRepository(db),
        routes=build_route_service(db),
    )


def build_reference_service(db: Session) -> ReferenceService:
    return ReferenceService(airports=AirportRepository(db), airlines=AirlineRepository(db))
