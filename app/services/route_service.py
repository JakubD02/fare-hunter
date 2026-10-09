from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.airport import Airport
from app.models.route import Route
from app.models.user import User
from app.schemas.route import RouteCreate, RouteUpdate


def list_routes(db: Session, user: User) -> list[Route]:
    query = select(Route).where(Route.user_id == user.id).order_by(Route.created_at.desc())

    return list(db.execute(query).scalars().all())


def get_route(db: Session, user: User, route_id: int) -> Route | None:
    query = select(Route).where(Route.user_id == user.id, Route.id == route_id).order_by(Route.created_at.desc())

    return db.execute(query).scalar_one_or_none()


def create_route(db: Session, user: User, route_in: RouteCreate) -> Route:
    origin = db.execute(select(Airport).where(Airport.id == route_in.origin_id)).scalar_one_or_none()
    if not origin:
        raise LookupError(f"Origin airport with id {route_in.origin_id} not found")

    destination = db.execute(select(Airport).where(Airport.id == route_in.destination_id)).scalar_one_or_none()
    if not destination:
        raise LookupError(f"Destination airport with id {route_in.destination_id} not found")

    if route_in.origin_id == route_in.destination_id:
        raise ValueError("origin_id and destination_id must be different")

    route = Route(
        user_id=user.id,
        origin_id=route_in.origin_id,
        destination_id=route_in.destination_id,
        departure_date=route_in.departure_date,
        return_date=route_in.return_date,
        is_active=route_in.is_active,
    )

    db.add(route)
    db.commit()
    db.refresh(route)
    return route


def update_route(db: Session, user: User, route_id: int, route_in: RouteUpdate) -> Route | None:
    route = get_route(db, user=user, route_id=route_id)
    if not route:
        return None

    data = route_in.model_dump(exclude_unset=True)

    for field, value in data.items():
        setattr(route, field, value)

    db.commit()
    db.refresh(route)
    return route


def remove_route(db: Session, user: User, route_id: int) -> bool:
    route = get_route(db, user=user, route_id=route_id)
    if not route:
        return False

    db.delete(route)
    db.commit()
    return True
