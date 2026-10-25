from datetime import datetime, timedelta
from decimal import Decimal

from app.enums.currency import Currency
from app.models.price_alert import PriceAlert


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
    if alert.last_notified_at and now - alert.last_notified_at < timedelta(hours=24):
        return False
    return True
