from app.celery_app import celery_app
from celery import shared_task
from sqlalchemy import select
from app.database import SessionLocal
from app.models.airline import Airline
from app.models.flight_price import FlightPrice
from app.models.route import Route
from app.services.serpapi_mock import fetch_prices


@shared_task
def fetch_prices_for_route(route_id: int) -> int:
    db = SessionLocal()
    try:
        stmt = select(Route).where(Route.id==route_id)
        route = db.execute(stmt).scalar_one_or_none()
        if not route:
            return 0

        airline_ids = list(db.execute(select(Airline.id)).scalars().all())
        if not airline_ids:
            return 0

        prices_data = fetch_prices(
            origin_code=route.origin.code,
            destination_code=route.destination.code,
            departure_date=route.departure_date,
            return_date=route.return_date,
            airlines_id=airline_ids,
        )

        saved_count = 0
        for price_data in prices_data:
            flight_price = FlightPrice(
                route_id=route.id,
                **price_data,
            )
            db.add(flight_price)
            saved_count += 1

        db.commit()
        return saved_count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()