from datetime import datetime, timedelta, timezone

from fastapi import logger, requests
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import TaskExecutionError
from app.models.flight_price import FlightPrice
from app.models.user import User
from app.services import routes_service


class FlightPriceService:
    def __init__(self):
        self.api_key = settings.SERPAPI_KEY
        self.base_url = settings.SERPAPI_URL

    def fetch_flight_price(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str | None = None,
    ) -> dict | None:
        """
        Fetch flight price from SerpAPI

        Args:
            origin: IATA code (e.g., "JFK")
            destination: IATA code (e.g., "LHR")
            departure_date: ISO format (e.g., "2026-10-01")
            return_date: ISO format or None for one-way

        Returns:
            {"price": float, "airline": str, "currency": str} or None
        """

        try:
            params = {
                "engine": "google_flights",
                "departure_id": origin,
                "arrival_id": destination,
                "outbound_date": departure_date,
                "type": "1" if not return_date else "2",
                "api_key": self.api_key,
            }

            if return_date:
                params["return_date"] = return_date

            logger.info(f"Fetching price: {origin} → {destination} on {departure_date}")

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "error" in data:
                logger.error(f"SerpAPI error: {data['error']}")
                raise TaskExecutionError(f"SerpAPI error: {data['error']}")

            best_price = self._extract_best_price(data)

            if not best_price:
                logger.warning(f"No price found for {origin} → {destination}")
                return None

            logger.info(f"Found price: ${best_price['price']} {best_price['currency']}")
            return best_price

        except requests.exceptions.Timeout as exc:
            logger.error(f"SerpAPI timeout: {exc}")
            raise TaskExecutionError(f"SerpAPI timeout: {exc}") from exc

        except requests.exceptions.RequestException as exc:
            logger.error(f"SerpAPI network error: {exc}")
            raise TaskExecutionError(f"SerpAPI network error: {exc}") from exc

        except Exception as exc:
            logger.error(f"Unexpected error: {exc}")
            raise

    def _extract_best_price(self, data: dict) -> dict | None:
        try:
            # structure: data["best_flights"][0]["price"]
            if "best_flights" not in data or not data["best_flights"]:
                return None

            best = data["best_flights"][0]

            return {
                "price": best.get("price", 0),
                "airline": best.get("airline", "Unknown"),
                "currency": data.get("currency", "USD"),
            }

        except (KeyError, IndexError, TypeError) as exc:
            logger.error(f"Error parsing SerpAPI response: {exc}")
            return None


def get_history(db: Session, user: User, route_id: int) -> list[FlightPrice] | None:
    route = routes_service.get_route(db=db, user=user, route_id=route_id)
    if not route:
        return None

    query = (
        select(FlightPrice)
        .where(FlightPrice.route_id == route_id)
        .order_by(FlightPrice.fetched_at.desc())
    )

    return list(db.execute(query).scalars().all())


def get_stats(
    db: Session, user: User, route_id: int, days: int = 30
) -> list[FlightPrice] | None:
    route = routes_service.get_route(db=db, user=user, route_id=route_id)
    if not route:
        return None

    since = datetime.now(timezone.utc) - timedelta(days=days)

    query = select(
        func.min(FlightPrice.price).label("min_price"),
        func.max(FlightPrice.price).label("max_price"),
        func.avg(FlightPrice.price).label("avg_price"),
        func.count(FlightPrice.price).label("sample_count"),
    ).where(
        FlightPrice.route_id == route_id,
        FlightPrice.fetched_at >= since,
    )

    result = db.execute(query).one()

    return {
        "route_id": route_id,
        "period_days": days,
        "sample_count": result.sample_count,
        "min_price": result.min_price,
        "max_price": result.max_price,
        "avg_price": result.avg_price,
    }


flight_price_service = FlightPriceService()
