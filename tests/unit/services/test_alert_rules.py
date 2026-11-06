from datetime import datetime, timedelta, timezone
from decimal import Decimal

from app.models.price_alert import PriceAlert
from app.services.alert_rules import should_notify

NOW = datetime(2026, 11, 2, 12, 0, tzinfo=timezone.utc)
THRESHOLD = Decimal("500.00")
SAME_CURRENCY = Decimal(1)
PLN_TO_EUR = Decimal("0.23")


def make_alert(last_notified_at: datetime | None = None) -> PriceAlert:
    return PriceAlert(threshold_price=THRESHOLD, last_notified_at=last_notified_at)


def test_should_notify_when_price_below_threshold_and_never_notified() -> None:
    alert = make_alert()

    assert should_notify(alert, Decimal("450.00"), SAME_CURRENCY, NOW) is True


def test_should_not_notify_when_price_above_threshold() -> None:
    alert = make_alert()

    assert should_notify(alert, Decimal("2400.00"), PLN_TO_EUR, NOW) is False


def test_should_not_notify_when_price_equals_threshold() -> None:
    alert = make_alert()

    assert should_notify(alert, THRESHOLD, SAME_CURRENCY, NOW) is False


def test_should_not_notify_during_cooldown() -> None:
    alert = make_alert(last_notified_at=NOW - timedelta(hours=1))

    assert should_notify(alert, Decimal("450.00"), SAME_CURRENCY, NOW) is False


def test_should_notify_after_cooldown_expired() -> None:
    alert = make_alert(last_notified_at=NOW - timedelta(hours=25))

    assert should_notify(alert, Decimal("450.00"), SAME_CURRENCY, NOW) is True


def test_should_notify_exactly_when_cooldown_ends() -> None:
    alert = make_alert(last_notified_at=NOW - timedelta(hours=24))

    assert should_notify(alert, Decimal("450.00"), SAME_CURRENCY, NOW) is True


def test_conversion_is_applied_not_raw_price() -> None:
    # Raw 450 would pass, but 450 PLN * 2 = 900 > 500, so it must not notify
    alert = make_alert()

    assert should_notify(alert, Decimal("450.00"), Decimal(2), NOW) is False


def test_should_notify_when_converted_price_below_threshold_but_raw_price_above() -> None:
    # Source PLN, route EUR: 2000 PLN * 0.23 = 460 EUR < 500 EUR.
    # The old raw check (2000 >= 500) wrongly suppressed this alert.
    alert = make_alert()

    assert should_notify(alert, Decimal("2000.00"), PLN_TO_EUR, NOW) is True


def test_should_not_notify_during_cooldown_even_if_converted_price_qualifies() -> None:
    alert = make_alert(last_notified_at=NOW - timedelta(hours=1))

    assert should_notify(alert, Decimal("2000.00"), PLN_TO_EUR, NOW) is False


def test_naive_last_notified_at_is_treated_as_utc() -> None:
    naive_recent = (NOW - timedelta(hours=2)).replace(tzinfo=None)
    alert = make_alert(last_notified_at=naive_recent)

    assert should_notify(alert, Decimal("450.00"), SAME_CURRENCY, NOW) is False
