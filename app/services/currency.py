from datetime import date
from decimal import Decimal

import httpx

from app.enums.currency import Currency

BASE_URL = "https://api.frankfurter.dev/v2"

_cache: dict[tuple[Currency, Currency, date], Decimal] = {}


def get_rate(base: Currency, quote: Currency) -> Decimal:
    key = (base, quote, date.today())
    if key not in _cache:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{BASE_URL}/rate/{base}/{quote}")
            response.raise_for_status()
        _cache[key] = Decimal(str(response.json()["rate"]))
    return _cache[key]


def convert(amount: Decimal, base: Currency, quote: Currency) -> Decimal:
    if base == quote:
        return amount
    return (amount * get_rate(base, quote)).quantize(Decimal("0.01"))
