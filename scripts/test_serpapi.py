from datetime import date, timedelta

from app.core.config import settings
from app.services.serpapi_provider import SerpApiFlightProvider


def main() -> None:
    provider = SerpApiFlightProvider(
        api_key=settings.SERPAPI_KEY,
        base_url=settings.SERPAPI_URL,
    )

    offers = provider.fetch_offers(
        origin_code="WAW",
        destination_code="LHR",
        departure_date=date.today() + timedelta(days=30),
    )

    print(f"Number of offers: {len(offers)}")

    for offer in offers[:5]:
        print(f"Airline: {offer['airline']}, price: {offer['price']} {offer['currency']}")


if __name__ == "__main__":
    main()
