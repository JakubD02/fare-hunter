from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.flight_price import FlightPrice
from app.models.user import User
from app.repositories.airline_repository import AirlineRepository
from app.repositories.flight_price_repository import FlightPriceRepository
from app.services.flight_price_provider import FlightOffer, FlightPriceProvider
from app.services.route_service import RouteService


class FlightPriceService:
    def __init__(
        self,
        prices: FlightPriceRepository,
        airlines: AirlineRepository,
        routes: RouteService,
        provider: FlightPriceProvider | None = None,
    ) -> None:
        self._prices = prices
        self._airlines = airlines
        self._routes = routes
        self._provider = provider

    def get_history(self, user: User, route_id: str) -> list[FlightPrice] | None:
        if self._routes.get_route(user, route_id) is None:
            return None
        return self._prices.list_for_route(route_id)

    def get_stats(self, user: User, route_id: str, days: int = 30) -> dict | None:
        if self._routes.get_route(user, route_id) is None:
            return None

        since = datetime.now(timezone.utc) - timedelta(days=days)
        aggregates = self._prices.aggregate_since(route_id, since)

        return {
            "route_id": route_id,
            "period_days": days,
            "sample_count": aggregates["sample_count"],
            "currency": self._prices.latest_currency(route_id),
            "min_price": aggregates["min_price"],
            "max_price": aggregates["max_price"],
            "avg_price": aggregates["avg_price"],
        }

    def refresh_prices(self, user: User, route_id: str) -> list[FlightPrice] | None:
        if self._provider is None:
            raise RuntimeError("FlightPriceService was created without a provider")
        route = self._routes.get_route(user, route_id)
        if route is None:
            return None

        offers = self._provider.fetch_offers(
            origin_code=route.origin_id,
            destination_code=route.destination_id,
            departure_date=route.departure_date,
            return_date=route.return_date,
        )
        return [self._prices.add(self._to_price(route_id, offer)) for offer in offers]

    def _to_price(self, route_id: str, offer: FlightOffer) -> FlightPrice:
        airline_id = self._airlines.find_id(offer["airline"])
        return FlightPrice(
            route_id=route_id,
            airline_id=airline_id,
            price=Decimal(offer["price"]),
            currency=offer["currency"],
        )
