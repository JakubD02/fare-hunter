from decimal import Decimal

import httpx

from app.enums.currency import Currency

BASE_URL = "https://api.frankfurter.dev/v2"


def get_rate(base: Currency, quote: Currency) -> Decimal:
    url = f"{BASE_URL}/rate/{base}/{quote}"
    with httpx.Client(timeout=5.0) as client:
        response = client.get(url)
        response.raise_for_status()
    data = response.json()
    return Decimal(data["rate"])


def convert(amount: Decimal, base: Currency, quote: Currency) -> Decimal:
    if base == quote:
        return amount
    return (amount * get_rate(base, quote)).quantize(Decimal("0.01"))
