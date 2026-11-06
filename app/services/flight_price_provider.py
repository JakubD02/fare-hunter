from datetime import date, time
from decimal import Decimal
from typing import Protocol, TypedDict

from app.enums.currency import Currency


class FlightOffer(TypedDict):
    airline: str
    price: Decimal
    currency: Currency
    duration: int
    origin_code: str
    destination_code: str
    departure_date: date
    departure_time: time | None
    return_date: date | None


class FlightPriceProvider(Protocol):
    def fetch_offers(
        self,
        origin_code: str,
        destination_code: str,
        departure_date: date,
        return_date: date | None = None,
        currency: Currency = Currency.PLN,
    ) -> list[FlightOffer]: ...
