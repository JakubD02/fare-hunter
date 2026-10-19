import logging

from app.api.v1.schemas.route import RouteCreate, RouteUpdate
from app.models.airport import Airport
from app.models.route import Route
from app.models.user import User
from app.repositories.airport_repository import AirportRepository
from app.repositories.route_repository import RouteRepository

logger = logging.getLogger(__name__)


class RouteService:
    def __init__(self, routes: RouteRepository, airports: AirportRepository) -> None:
        self._routes = routes
        self._airports = airports

    def list_routes(self, user: User) -> list[Route]:
        routes = self._routes.list_for_user(user)
        logger.debug("routes listed user_id=%s count=%d", user.id, len(routes))
        return routes

    def get_route(self, user: User, route_id: str) -> Route | None:
        route = self._routes.get_for_user(user, route_id)
        logger.debug("route lookup route_id=%s user_id=%s found=%s", route_id, user.id, route is not None)
        return route

    def create_route(self, user: User, route_in: RouteCreate) -> Route:
        origin = self._get_airport(route_in.origin_id)
        destination = self._get_airport(route_in.destination_id)
        self._validate_airports_different(origin, destination)

        route = Route(
            user_id=user.id,
            origin_id=origin.id,
            destination_id=destination.id,
            departure_date=route_in.departure_date,
            return_date=route_in.return_date,
            is_active=route_in.is_active,
        )
        route = self._routes.add(route)
        logger.info(
            "route created id=%s user_id=%s %s->%s departure=%s",
            route.id,
            user.id,
            origin.id,
            destination.id,
            route.departure_date,
        )
        return route

    def update_route(self, user: User, route_id: str, route_in: RouteUpdate) -> Route | None:
        route = self._routes.get_for_user(user, route_id)
        if route is None:
            logger.warning("route update rejected: not found route_id=%s user_id=%s", route_id, user.id)
            return None

        data = route_in.model_dump(exclude_unset=True)

        departure_date = data.get("departure_date", route.departure_date)
        return_date = data.get("return_date", route.return_date)
        if return_date is not None and return_date < departure_date:
            logger.warning("route update rejected: return before departure route_id=%s", route_id)
            raise ValueError("Return date must not be before departure date")

        origin = self._get_airport(data.get("origin_id", route.origin_id))
        destination = self._get_airport(data.get("destination_id", route.destination_id))
        self._validate_airports_different(origin, destination)

        for field, value in data.items():
            setattr(route, field, value)

        route.origin_id = origin.id
        route.destination_id = destination.id

        route = self._routes.save(route)
        logger.info(
            "route updated id=%s user_id=%s fields=%s",
            route_id,
            user.id,
            sorted(data.keys()),
        )
        return route

    def remove_route(self, user: User, route_id: str) -> bool:
        route = self._routes.get_for_user(user, route_id)
        if route is None:
            logger.info("route remove skipped: not found route_id=%s user_id=%s", route_id, user.id)
            return False

        self._routes.delete(route)
        logger.info("route removed id=%s user_id=%s", route_id, user.id)
        return True

    def _get_airport(self, airport_id: str) -> Airport:
        airport_id = airport_id.strip()
        if not airport_id:
            logger.warning("route rejected: empty airport id")
            raise LookupError("Airport ID cannot be empty")

        airport = self._airports.get_by_id(airport_id)
        if airport is None:
            logger.warning("route rejected: airport not found id=%s", airport_id)
            raise LookupError(f"Airport with ID {airport_id} not found")

        return airport

    @staticmethod
    def _validate_airports_different(origin: Airport, destination: Airport) -> None:
        if origin.id == destination.id:
            logger.warning("route rejected: same origin and destination id=%s", origin.id)
            raise ValueError("Origin and destination must be different airports")
