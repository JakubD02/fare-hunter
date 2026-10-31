import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.flight_price import FlightPrice
from app.models.user import User
from app.repositories.airline_repository import AirlineRepository
from app.repositories.flight_price_repository import FlightPriceRepository
from app.services.flight_price_provider import FlightOffer, FlightPriceProvider
from app.services.route_service import RouteService

logger = logging.getLogger(__name__)


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

    def get_history(self, user: User, route_id: str, limit: int, offset: int) -> list[FlightPrice] | None:
        if self._routes.get_route(user, route_id) is None:
            logger.warning("history rejected: route not found route_id=%s user_id=%s", route_id, user.id)
            return None
        history = self._prices.list_for_route(route_id, limit=limit, offset=offset)
        logger.debug("history loaded route_id=%s rows=%d", route_id, len(history))
        return history

    def get_stats(
        self, user: User, route_id: str, days: int = 30, preferred_currency: str | None = None
    ) -> dict | None:
        if self._routes.get_route(user, route_id) is None:
            logger.warning("stats rejected: route not found route_id=%s user_id=%s", route_id, user.id)
            return None

        since = datetime.now(timezone.utc) - timedelta(days=days)
        by_currency = self._prices.aggregate_since(route_id, since)
        logger.debug(
            "stats computed route_id=%s days=%d currencies=%d",
            route_id,
            days,
            len(by_currency),
        )

        if preferred_currency is not None:
            by_currency.sort(key=lambda row: row["currency"] != preferred_currency)

        primary = by_currency[0] if by_currency else None

        return {
            "route_id": route_id,
            "period_days": days,
            "currency": primary["currency"] if primary else None,
            "sample_count": primary["sample_count"] if primary else 0,
            "min_price": primary["min_price"] if primary else None,
            "max_price": primary["max_price"] if primary else None,
            "avg_price": primary["avg_price"] if primary else None,
            "by_currency": by_currency,
        }

    def refresh_prices(self, user: User, route_id: str) -> list[FlightPrice] | None:
        if self._provider is None:
            raise RuntimeError("FlightPriceService was created without a provider")
        route = self._routes.get_route(user, route_id)
        if route is None:
            logger.warning("refresh rejected: route not found route_id=%s user_id=%s", route_id, user.id)
            return None

        logger.info(
            "refresh started route_id=%s %s->%s departure=%s return=%s",
            route_id,
            route.origin_id,
            route.destination_id,
            route.departure_date,
            route.return_date,
        )

        offers = self._provider.fetch_offers(
            origin_code=route.origin_airport.iata_code,
            destination_code=route.destination_airport.iata_code,
            departure_date=route.departure_date,
            return_date=route.return_date,
        )
        if not offers:
            logger.warning("refresh got no offers route_id=%s", route_id)
            return []

        saved: list[FlightPrice] = []
        for offer in offers:
            try:
                price = self._to_price(route_id, offer)
                if price is None:
                    continue
                saved.append(self._prices.add(price))
            except Exception:
                logger.exception(
                    "failed to save offer airline=%s route_id=%s",
                    offer.get("airline"),
                    route_id,
                )
        return saved

    def _to_price(self, route_id: str, offer: FlightOffer) -> FlightPrice | None:
        airline_id = self._airlines.find_id(offer["airline"])
        if airline_id is None:
            logger.warning("unknown airline in offer airline=%s route_id=%s", offer["airline"], route_id)
            return None
        return FlightPrice(
            route_id=route_id,
            airline_id=airline_id,
            price=Decimal(offer["price"]),
            currency=offer["currency"],
        )
