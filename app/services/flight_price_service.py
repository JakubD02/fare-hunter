from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.flight_price import FlightPrice
from app.models.user import User
from app.services import routes_service


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
