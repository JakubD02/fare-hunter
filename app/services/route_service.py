from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.airport import Airport
from app.models.route import Route
from app.models.user import User
from app.schemas.route import RouteCreate, RouteUpdate


def _validate_route_airports(db: Session, origin_id: str, destination_id: str) -> tuple[Airport, Airport]:
    if origin_id == destination_id:
        raise ValueError("origin_id and destination_id must be different")

    origin = db.execute(select(Airport).where(Airport.id == origin_id)).scalar_one_or_none()
    if not origin:
        raise LookupError(f"Origin airport with id {origin_id} not found")

    destination = db.execute(select(Airport).where(Airport.id == destination_id)).scalar_one_or_none()
    if not destination:
        raise LookupError(f"Destination airport with id {destination_id} not found")

    return origin, destination


def list_routes(db: Session, user: User) -> list[Route]:
    query = select(Route).where(Route.user_id == user.id).order_by(Route.created_at.desc())

    return list(db.execute(query).scalars().all())


def get_route(db: Session, user: User, route_id: str) -> Route | None:
    query = select(Route).where(Route.user_id == user.id, Route.id == route_id).order_by(Route.created_at.desc())

    return db.execute(query).scalar_one_or_none()


def create_route(db: Session, user: User, route_in: RouteCreate) -> Route:
    origin, destination = _validate_route_airports(db, route_in.origin_id, route_in.destination_id)

    route = Route(
        user_id=user.id,
        origin_id=origin.id,
        destination_id=destination.id,
        departure_date=route_in.departure_date,
        return_date=route_in.return_date,
        is_active=route_in.is_active,
    )

    db.add(route)
    db.commit()
    db.refresh(route)
    return route


def update_route(db: Session, user: User, route_id: str, route_in: RouteUpdate) -> Route | None:
    route = get_route(db, user=user, route_id=route_id)
    if not route:
        return None

    data = route_in.model_dump(exclude_unset=True)

    origin_id = data.get("origin_id", route.origin_id)
    destination_id = data.get("destination_id", route.destination_id)
    if origin_id is None or destination_id is None:
        raise ValueError("origin_id and destination_id cannot be null")

    _validate_route_airports(db, origin_id, destination_id)

    for field, value in data.items():
        setattr(route, field, value)

    db.commit()
    db.refresh(route)
    return route


def remove_route(db: Session, user: User, route_id: str) -> bool:
    route = get_route(db, user=user, route_id=route_id)
    if not route:
        return False

    db.delete(route)
    db.commit()
    return True
