from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.airport import Airport
from app.models.route import Route
from app.models.user import User
from app.schemas.route import RouteCreate, RouteUpdate


def _get_airport_by_id(db: Session, airport_id: str) -> Airport:
    airport_id = airport_id.strip()
    if not airport_id:
        raise LookupError("Airport ID cannot be empty")

    airport = db.get(Airport, airport_id)

    if airport is None:
        raise LookupError(f"Airport with ID {airport_id} not found")

    return airport


def _validate_airports_different(origin: Airport, destination: Airport) -> None:
    """Ensure origin and destination are different airports"""
    if origin.id == destination.id:
        raise ValueError("Origin and destination must be different airports")


def list_routes(db: Session, user: User) -> list[Route]:
    query = select(Route).where(Route.user_id == user.id).order_by(Route.created_at.desc())

    return list(db.execute(query).scalars().all())


def get_route(db: Session, user: User, route_id: str) -> Route | None:
    query = select(Route).where(Route.user_id == user.id, Route.id == route_id).order_by(Route.created_at.desc())

    return db.execute(query).scalar_one_or_none()


def create_route(db: Session, user: User, route_in: RouteCreate) -> Route:
    origin = _get_airport_by_id(db, route_in.origin_id)
    destination = _get_airport_by_id(db, route_in.destination_id)
    _validate_airports_different(origin, destination)

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

    departure_date = data.get("departure_date", route.departure_date)
    return_date = data.get("return_date", route.return_date)

    if return_date is not None and return_date < departure_date:
        raise ValueError("Return date must not be before departure date")

    origin_id = data.get("origin_id", route.origin_id)
    destination_id = data.get("destination_id", route.destination_id)

    origin = _get_airport_by_id(db, origin_id)
    destination = _get_airport_by_id(db, destination_id)

    _validate_airports_different(origin, destination)

    for field, value in data.items():
        setattr(route, field, value)

    if "origin_id" in data:
        route.origin_id = origin.id
    if "destination_id" in data:
        route.destination_id = destination.id

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
