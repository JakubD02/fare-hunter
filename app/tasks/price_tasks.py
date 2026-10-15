import logging
from decimal import Decimal

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.celery_app import celery_app
from app.core.exceptions import TaskExecutionError
from app.database import SessionLocal
from app.enums.currency import Currency
from app.models.airline import Airline
from app.models.flight_price import FlightPrice
from app.models.price_alert import PriceAlert
from app.models.route import Route
from app.services import currency as currency_service
from app.services.flight_price_service import flight_price_service
from app.tasks.email_tasks import send_price_drop_email_task

logger = logging.getLogger(__name__)


def _find_airline_id(db: Session, airline_name: str | None) -> str | None:
    if not airline_name:
        return None
    stmt = select(Airline.id).where((Airline.iata_code == airline_name) | (Airline.name == airline_name))
    return db.execute(stmt).scalar_one_or_none()


@celery_app.task(bind=True)
def fetch_prices_for_route(self, route_id: str) -> int:
    db = SessionLocal()
    try:
        stmt = select(Route).where(Route.id == route_id)
        route = db.execute(stmt).scalar_one_or_none()
        if not route:
            return 0

        price_data = flight_price_service.fetch_flight_price(
            origin=route.origin_airport.iata_code,
            destination=route.destination_airport.iata_code,
            departure_date=route.departure_date.isoformat(),
        )

        if not price_data:
            logger.warning(f"No price found for route {route_id}")
            return 0

        try:
            flight_currency = Currency(price_data["currency"])
        except ValueError:
            logger.error(f"Unsupported currency {price_data['currency']} for route {route_id}")
            return 0

        price = Decimal(str(price_data["price"]))

        airline_id = _find_airline_id(db, price_data.get("airline"))
        if airline_id is None:
            logger.warning(f"Unknown airline {price_data.get('airline')!r} for route {route_id}")
            return 0

        flight_price = FlightPrice(
            route_id=route.id,
            price=price,
            currency=flight_currency,
            airline_id=airline_id,
            departure_date=route.departure_date,
            return_date=route.return_date,
        )
        db.add(flight_price)
        db.commit()
        logger.info(f"Saved price for route {route_id}")

        alert_stmt = select(PriceAlert).where((PriceAlert.route_id == route_id) & (PriceAlert.is_active))
        alert = db.execute(alert_stmt).scalar_one_or_none()
        if not alert:
            return 1

        alert_currency = Currency(alert.currency)
        new_price = currency_service.convert(price, flight_currency, alert_currency)

        if new_price < alert.threshold_price:
            logger.warning(f"Price drop! {new_price} {alert_currency} < {alert.threshold_price} {alert_currency}")

            prev_price_stmt = (
                select(FlightPrice)
                .where((FlightPrice.route_id == route_id) & (FlightPrice.id != flight_price.id))
                .order_by(FlightPrice.fetched_at.desc())
                .limit(1)
            )
            prev = db.execute(prev_price_stmt).scalar_one_or_none()
            old_price = currency_service.convert(prev.price, prev.currency, alert_currency) if prev else new_price

            send_price_drop_email_task.delay(
                user_id=str(route.user_id),
                route_id=route.id,
                old_price=float(old_price),
                new_price=float(new_price),
            )

        return 1

    except (TaskExecutionError, httpx.HTTPError) as e:
        logger.error(f"Network or API error: {e}")
        self.retry(exc=e, countdown=300)
        return 0

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        db.rollback()
        raise

    finally:
        db.close()


@celery_app.task
def fetch_all_prices_periodic() -> int:
    db = SessionLocal()
    try:
        stmt = select(Route).join(PriceAlert).where(PriceAlert.is_active).distinct()
        routes = db.execute(stmt).scalars().all()

        logger.info(f"Found {len(routes)} routes with alerts")

        count = 0
        for route in routes:
            fetch_prices_for_route.delay(route_id=str(route.id))
            count += 1

        logger.info(f"Queued {count} price fetch tasks")
        return count

    except Exception as exc:
        logger.error(f"Error: {exc}")
        raise

    finally:
        db.close()
