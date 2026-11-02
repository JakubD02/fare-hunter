from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.enums.currency import Currency
from app.models.price_alert import PriceAlert
from app.services.alert_rules import should_notify

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
THRESHOLD = Decimal("500.00")


def make_alert(last_notified_at: datetime | None = None) -> PriceAlert:
    return PriceAlert(threshold_price=THRESHOLD, last_notified_at=last_notified_at)


def test_should_notify_when_price_below_threshold_and_never_notified() -> None:
    alert = make_alert()

    assert should_notify(alert, Decimal("450.00"), Currency.PLN, Currency.PLN, NOW) is True


def test_should_not_notify_when_price_above_threshold() -> None:
    alert = make_alert()

    assert should_notify(alert, Decimal("550.00"), Currency.PLN, Currency.PLN, NOW) is False


def test_should_not_notify_when_price_equals_threshold() -> None:
    alert = make_alert()

    assert should_notify(alert, THRESHOLD, Currency.PLN, Currency.PLN, NOW) is False


def test_should_not_notify_during_cooldown() -> None:
    alert = make_alert(last_notified_at=NOW - timedelta(hours=1))

    assert should_notify(alert, Decimal("450.00"), Currency.PLN, Currency.PLN, NOW) is False


def test_should_notify_after_cooldown_expired() -> None:
    alert = make_alert(last_notified_at=NOW - timedelta(hours=25))

    assert should_notify(alert, Decimal("450.00"), Currency.PLN, Currency.PLN, NOW) is True


def test_should_notify_exactly_when_cooldown_ends() -> None:
    alert = make_alert(last_notified_at=NOW - timedelta(hours=24))

    assert should_notify(alert, Decimal("450.00"), Currency.PLN, Currency.PLN, NOW) is True


def test_should_not_notify_when_currency_mismatch() -> None:
    alert = make_alert()

    assert should_notify(alert, Decimal("100.00"), Currency.EUR, Currency.PLN, NOW) is False
