
# majac origin + destination code, departure, return date, airlines id
# tworzymy liste z M slownikami z powyzszymi danymi
# sortujemy je po cenie i zwracamy N rekordow

from datetime import date
from decimal import Decimal
import random

from app.constants.mock import MOCK_TOTAL_GENERATED, MOCK_PRICE_MIN, MOCK_PRICE_MAX, MOCK_NUM_RESULTS
from app.enums.currency import Currency


def fetch_prices(
        origin_code: str,
        destination_code: str,
        departure_date: date,
        return_date: date,
        airlines_id: list[int],
) -> list[dict]:
    """Generate fake flight prices"""
    all_prices = []
    for i in range(MOCK_TOTAL_GENERATED):
        all_prices.append(
            {
                "airline_id": random.choice(airlines_id),
                "price": Decimal(str(round(random.uniform(MOCK_PRICE_MIN, MOCK_PRICE_MAX), 2))),
                "currency": Currency.PLN,
                "origin_code": origin_code,
                "departure_date": departure_date,
                "return_date": return_date,
            }
        )

    all_prices.sort(key=lambda p: p["price"])
    return all_prices[:MOCK_NUM_RESULTS]