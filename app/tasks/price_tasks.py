import logging
from datetime import datetime, timezone
from decimal import Decimal

import httpx

from app.celery_app import celery_app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.flight_price import FlightPrice
from app.repositories.airline_repository import AirlineRepository
from app.repositories.airport_repository import AirportRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.user_repository import UserRepository
from app.services.alert_service import AlertService
from app.services.reference_service import ReferenceService
from app.services.route_service import RouteService
from app.services.serpapi_provider import SerpApiFlightProvider
from app.tasks.email_tasks import send_price_drop_email_task

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True, max_retries=3, autoretry_for=(httpx.TransportError,), retry_backoff=True, retry_backoff_max=30
)
def fetch_prices_for_route(self, route_id: str, user_id: str) -> int:
    with SessionLocal() as db:
        user_repository = UserRepository(db)
        user = user_repository.get_by_id(user_id)
        if user is None:
            logger.warning("User not found: %s", user_id)
            return 0

        route_service = RouteService(
            routes=RouteRepository(db),
            airports=AirportRepository(db),
        )

        route = route_service.get_route(user=user, route_id=route_id)
        if route is None or not route.is_active:
            logger.warning("Failed to enqueue price fetch: route_id=%s user_id=%s", route_id, user_id)
            return 0

        provider = SerpApiFlightProvider(api_key=settings.SERPAPI_KEY, base_url=settings.SERPAPI_URL)
        offers = provider.fetch_offers(
            origin_code=route.origin_airport.iata_code,
            destination_code=route.destination_airport.iata_code,
            departure_date=route.departure_date,
            return_date=route.return_date,
            currency=route.currency,
        )
        if not offers:
            logger.warning("No offers for route %s", route_id)
            return 0

        best = min(offers, key=lambda offer: offer["price"])

        airline_id = ReferenceService(airports=AirportRepository(db), airlines=AirlineRepository(db)).find_airline_id(
            best["airline"]
        )
        if airline_id is None:
            logger.warning("Unknown airline %r for route %s", best["airline"], route_id)
            return 0

        flight_price = FlightPrice(
            route_id=route.id,
            airline_id=airline_id,
            price=Decimal(str(best["price"])),
            currency=best["currency"],
            departure_date=route.departure_date,
            return_date=route.return_date,
        )
        db.add(flight_price)

        should_send = AlertService(AlertRepository(db), route_service).check_price(
            route=route, flight_price=flight_price, now=datetime.now(timezone.utc)
        )
        db.commit()

        if should_send:
            send_price_drop_email_task.delay(
                route_id=str(route.id),
                user_id=str(route.user_id),
                price=str(flight_price.price),
            )

        logger.info("Saved price %s %s for route %s", flight_price.price, flight_price.currency, route_id)
        return 1


@celery_app.task
def fetch_all_prices_periodic() -> int:
    today = datetime.now(timezone.utc).date()

    with SessionLocal() as db:
        targets = RouteRepository(db).list_tracking_targets(today)
    queued = 0
    for route_id, user_id in targets:
        try:
            route_id, user_id = str(route_id), str(user_id)
            fetch_prices_for_route.delay(route_id=route_id, user_id=user_id)
            queued += 1
        except Exception:
            logger.exception(
                "Failed to enqueue price fetch: route_id=%s user_id=%s",
                route_id,
                user_id,
            )

    logger.info("Queued price fetch tasks: %d/%d", queued, len(targets))

    return queued
