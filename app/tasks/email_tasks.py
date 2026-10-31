import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.exceptions import EmailSendError
from app.enums.currency import Currency
from app.models.price_alert import PriceAlert
from app.models.route import Route
from app.models.user import User
from app.services.alert_rules import should_notify
from app.services.email_service import AlertAction, EmailService
from app.services.factories import build_alert_service, build_route_service, build_user_service

logger = logging.getLogger(__name__)

EMAIL_RETRY_OPTIONS = {
    "autoretry_for": (EmailSendError,),
    "retry_backoff": True,
    "retry_backoff_max": 300,
    "max_retries": 3,
}


def _load_alert_context(db: Session, user_id: str, route_id: str) -> tuple[User, PriceAlert, Route] | None:
    user = build_user_service(db).get_by_id(user_id)
    if user is None:
        logger.warning("Email skipped: user not found user_id=%s", user_id)
        return None

    alert = build_alert_service(db).get_alert(user, route_id)
    if alert is None:
        logger.warning("Email skipped: alert not found route_id=%s user_id=%s", route_id, user_id)
        return None

    route = build_route_service(db).get_route(user, route_id)
    if route is None:
        logger.warning("Email skipped: route not found route_id=%s user_id=%s", route_id, user_id)
        return None

    return user, alert, route


def _route_label(route: Route) -> str:
    return f"{route.origin_airport.iata_code} → {route.destination_airport.iata_code}"


@celery_app.task(bind=True, **EMAIL_RETRY_OPTIONS)
def send_alert_confirmation_email_task(self, route_id: str, user_id: str, action: AlertAction) -> int:
    with SessionLocal() as db:
        context = _load_alert_context(db, user_id, route_id)
        if context is None:
            return 0
        user, alert, route = context

        EmailService().send_alert_confirmation(
            to_email=user.email,
            route_label=_route_label(route),
            threshold=alert.threshold_price,
            currency=route.currency.value,
            action=action,
        )

    logger.info("Confirmation sent route_id=%s user_id=%s action=%s", route_id, user_id, action)
    return 1


@celery_app.task(bind=True, **EMAIL_RETRY_OPTIONS)
def send_price_drop_email_task(self, route_id: str, user_id: str, price: str, price_currency: str) -> int:
    with SessionLocal() as db:
        context = _load_alert_context(db, user_id, route_id)
        if context is None:
            return 0
        user, alert, route = context

        now = datetime.now(timezone.utc)
        if not should_notify(alert, Decimal(price), Currency(price_currency), route.currency, now):
            logger.info("Price drop email skipped route_id=%s user_id=%s", route_id, user_id)
            return 0

        EmailService().send_price_drop_notification(
            to_email=user.email,
            route_label=_route_label(route),
            price=Decimal(price),
            threshold=alert.threshold_price,
            currency=route.currency.value,
        )

        build_alert_service(db).mark_notified(alert, now)

    logger.info("Price drop email sent route_id=%s user_id=%s", route_id, user_id)
    return 1
