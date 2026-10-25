from datetime import date

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

    def list_for_user(self, user: User, limit: int, offset: int) -> list[Route]:
        query = (
            select(Route).where(Route.user_id == user.id).order_by(Route.created_at.desc()).limit(limit).offset(offset)
        )
        return list(self._db.execute(query).scalars().all())

    def list_tracking_targets(self, today: date) -> list[tuple[str, str]]:
        query = (
            select(Route.id, Route.user_id)
            .where(Route.is_active.is_(True), Route.departure_date >= today)
            .order_by(Route.departure_date.asc())
        )
        rows = self._db.execute(query).all()

        return [(str(route_id), str(user_id)) for route_id, user_id in rows]

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
