from app.models.route import Route
from app.repositories.route_repository import RouteRepository


class FeaturedRouteService:
    """Read-only access to the public demo set. Never takes a user."""

    def __init__(self, routes: RouteRepository) -> None:
        self._routes = routes

    def list_featured(self, limit: int, offset: int) -> list[Route]:
        return self._routes.list_featured(limit=limit, offset=offset)

    def get_featured_route(self, route_id: str) -> Route | None:
        return self._routes.get_featured(route_id)
