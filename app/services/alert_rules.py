from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.enums.currency import Currency
from app.models.price_alert import PriceAlert

NOTIFICATION_COOLDOWN = timedelta(hours=24)


def _as_utc(value: datetime) -> datetime:
    """Treat naive datetimes as UTC (SQLite drops tzinfo)."""
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def should_notify(
    alert: PriceAlert,
    price: Decimal,
    price_currency: Currency,
    route_currency: Currency,
    now: datetime,
) -> bool:
    if price_currency != route_currency:
        return False
    if price >= alert.threshold_price:
        return False
    if alert.last_notified_at is not None and _as_utc(now) - _as_utc(alert.last_notified_at) < NOTIFICATION_COOLDOWN:
        return False
    return True
