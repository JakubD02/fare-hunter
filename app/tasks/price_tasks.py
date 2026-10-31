import logging
from datetime import datetime, timezone

import httpx

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.factories import (
    build_alert_service,
    build_flight_price_service,
    build_route_service,
    build_user_service,
)
from app.tasks.email_tasks import send_price_drop_email_task

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(httpx.TransportError, httpx.HTTPStatusError),
    retry_backoff=True,
    retry_backoff_max=30,
)
def fetch_prices_for_route(self, route_id: str, user_id: str) -> int:
    with SessionLocal() as db:
        user = build_user_service(db).get_by_id(user_id)
        if user is None:
            logger.warning("User not found: %s", user_id)
            return 0

        route = build_route_service(db).get_route(user=user, route_id=route_id)
        if route is None or not route.is_active:
            logger.warning("Route not found or inactive: route_id=%s user_id=%s", route_id, user_id)
            return 0

        prices = build_flight_price_service(db).refresh_prices(user=user, route_id=route.id)
        if not prices:
            logger.warning("No price saved for route %s", route_id)
            return 0

        flight_price = min(prices, key=lambda p: p.price)
        should_send = build_alert_service(db).check_price(
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
        targets = build_route_service(db).list_tracking_targets(today)
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
