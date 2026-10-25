from datetime import date
from decimal import Decimal

import httpx

from app.enums.currency import Currency
from app.services.flight_price_provider import FlightOffer


class SerpApiFlightProvider:
    def __init__(self, api_key: str, base_url: str, client: httpx.Client | None = None) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(timeout=10.0)

    def fetch_offers(
        self,
        origin_code: str,
        destination_code: str,
        departure_date: date,
        return_date: date | None = None,
        currency: Currency = Currency.PLN,
    ) -> list[FlightOffer]:
        params: dict[str, str] = {
            "engine": "google_flights",
            "departure_id": origin_code,
            "arrival_id": destination_code,
            "outbound_date": departure_date.isoformat(),
            "currency": currency.value,
            "type": "1" if return_date else "2",
            "api_key": self._api_key,
        }
        if return_date:
            params["return_date"] = return_date.isoformat()

        response = self._client.get(f"{self._base_url}/search.json", params=params)
        response.raise_for_status()
        data = response.json()

        offers: list[FlightOffer] = []
        for item in data.get("best_flights", []) + data.get("other_flights", []):
            flights = item.get("flights") or []
            if not flights or "price" not in item or "flight_number" not in flights[0]:
                continue
            offers.append(
                {
                    "airline": flights[0]["flight_number"].split()[0],
                    "price": Decimal(str(item["price"])),
                    "currency": currency,
                    "origin_code": origin_code,
                    "destination_code": destination_code,
                    "departure_date": departure_date,
                    "return_date": return_date,
                }
            )
        return offers
