from datetime import date
from decimal import Decimal
from typing import Protocol, TypedDict

from app.enums.currency import Currency


class FlightOffer(TypedDict):
    airline: str
    price: Decimal
    currency: Currency
    origin_code: str
    destination_code: str
    departure_date: date
    return_date: date | None


class FlightPriceProvider(Protocol):
    def fetch_offers(
        self,
        origin_code: str,
        destination_code: str,
        departure_date: date,
        return_date: date | None = None,
    ) -> list[FlightOffer]: ...
