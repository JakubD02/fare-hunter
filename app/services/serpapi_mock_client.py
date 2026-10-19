import logging
import random
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from app.constants.mock import (
    MOCK_NUM_RESULTS,
    MOCK_PRICE_MAX,
    MOCK_PRICE_MIN,
    MOCK_TOTAL_GENERATED,
)
from app.enums.currency import Currency
from app.services.flight_price_service import FlightOffer

logger = logging.getLogger(__name__)


class SerpApiMockClient:
    def __init__(self, airline_names: list[str], seed: int | None = None) -> None:
        if not airline_names:
            raise ValueError("airline_names cannot be empty")
        self._airline_names = airline_names
        self._rng = random.Random(seed)
        logger.info("mock flight client ready airlines=%s seed=%s", airline_names, seed)

    def fetch_offers(
        self,
        origin_code: str,
        destination_code: str,
        departure_date: date,
        return_date: date | None = None,
    ) -> list[FlightOffer]:
        logger.info("mock fetch %s->%s departure=%s", origin_code, destination_code, departure_date)
        offers = [
            FlightOffer(
                airline=self._rng.choice(self._airline_names),
                price=self._random_price(),
                currency=Currency.PLN,
                origin_code=origin_code,
                destination_code=destination_code,
                departure_date=departure_date,
                return_date=return_date,
            )
            for _ in range(MOCK_TOTAL_GENERATED)
        ]

        offers.sort(key=lambda offer: offer["price"])
        result = offers[:MOCK_NUM_RESULTS]
        logger.debug(
            "mock generated=%d returned=%d cheapest=%s",
            MOCK_TOTAL_GENERATED,
            len(result),
            result[0]["price"] if result else None,
        )
        return result

    def _random_price(self) -> Decimal:
        raw = self._rng.uniform(MOCK_PRICE_MIN, MOCK_PRICE_MAX)
        return Decimal(str(raw)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
