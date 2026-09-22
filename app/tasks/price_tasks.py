import logging

from sqlalchemy import select

from app.celery_app import celery_app
from app.core.exceptions import TaskExecutionError
from app.database import SessionLocal
from app.models.flight_price import FlightPrice
from app.models.price_alert import PriceAlert
from app.models.route import Route
from app.services.flight_price_service import flight_price_service
from app.tasks.email_tasks import send_price_drop_email_task

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def fetch_prices_for_route(self, route_id: int) -> int:
    db = SessionLocal()
    try:
        stmt = select(Route).where(Route.id == route_id)
        route = db.execute(stmt).scalar_one_or_none()
        if not route:
            return 0

        price_data = flight_price_service.fetch_flight_price(
            origin=route.origin.code,
            destination=route.destination.code,
            departure_date=route.departure_date.isoformat(),
        )

        if not price_data:
            logger.warning(f"No price found for route {route_id}")
            return 0

        flight_price = FlightPrice(
            route_id=route.id,
            price=price_data["price"],
            airline=price_data["airline"],
            currency=price_data["currency"],
        )
        db.add(flight_price)
        db.commit()
        logger.info(f"Saved price for route {route_id}")

        stmt = select(PriceAlert).where(
            PriceAlert.route_id == route_id,
            PriceAlert.is_active == True,
        )
        alert = db.execute(stmt).scalar_one_or_none()

        if not alert:
            return 1

        if price_data["price"] < alert.threshold_price:
            logger.warning(
                f"Price drop! ${price_data['price']} < ${alert.threshold_price}"
            )

            stmt = (
                select(FlightPrice)
                .where(
                    FlightPrice.route_id == route_id,
                    FlightPrice.id != flight_price.id,
                )
                .order_by(FlightPrice.created_at.desc())
                .limit(1)
            )

            prev = db.execute(stmt).scalar_one_or_none()
            old_price = prev.price if prev else price_data["price"]

            send_price_drop_email_task.delay(
                user_id=str(route.user_id),
                route_id=route.id,
                old_price=old_price,
                new_price=price_data["price"],
            )

            return 1

    except TaskExecutionError as e:
        logger.error(f"Network error: {e}")
        self.retry(exc=e, countdown=300)

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
        stmt = (
            select(Route)
            .join(PriceAlert)
            .where(PriceAlert.is_active == True)
            .distinct()
        )
        routes = db.execute(stmt).scalars().all()

        logger.info(f"Found {len(routes)} routes with alerts")

        count = 0
        for route in routes:
            fetch_prices_for_route.delay(route_id=route.id)
            count += 1

        logger.info(f"Queued {count} price fetch tasks")
        return count

    except Exception as exc:
        logger.error(f"Error: {exc}")
        raise

    finally:
        db.close()


# @shared_task
# def fetch_prices_for_route(route_id: int) -> int:
#     db = SessionLocal()
#     try:
#         stmt = select(Route).where(Route.id == route_id)
#         route = db.execute(stmt).scalar_one_or_none()
#         if not route:
#             return 0

#         airline_ids = list(db.execute(select(Airline.id)).scalars().all())
#         if not airline_ids:
#             return 0

#         prices_data = fetch_prices(
#             origin_code=route.origin.code,
#             destination_code=route.destination.code,
#             departure_date=route.departure_date,
#             return_date=route.return_date,
#             airlines_id=airline_ids,
#         )

#         saved_count = 0
#         for price_data in prices_data:
#             flight_price = FlightPrice(
#                 route_id=route.id,
#                 **price_data,
#             )
#             db.add(flight_price)
#             saved_count += 1

#         db.commit()
#         return saved_count
#     except Exception:
#         db.rollback()
#         raise
#     finally:
#         db.close()
