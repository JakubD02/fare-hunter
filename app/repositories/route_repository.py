from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.route import Route
from app.models.user import User


class RouteRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_for_user(self, user: User, route_id: str) -> Route | None:
        query = select(Route).where(Route.user_id == user.id, Route.id == route_id).order_by(Route.created_at.desc())
        return self._db.execute(query).scalar_one_or_none()

    def list_for_user(self, user: User) -> list[Route]:
        query = select(Route).where(Route.user_id == user.id).order_by(Route.created_at.desc())
        return list(self._db.execute(query).scalars().all())

    def add(self, route: Route) -> Route:
        self._db.add(route)
        self._db.commit()
        self._db.refresh(route)
        return route

    def save(self, route: Route) -> Route:
        self._db.commit()
        self._db.refresh(route)
        return route

    def delete(self, route: Route) -> None:
        self._db.delete(route)
        self._db.commit()
