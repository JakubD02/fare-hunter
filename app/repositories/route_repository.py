from datetime import date

from sqlalchemy import Select, select

from app.models.route import Route
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class RouteRepository(BaseRepository[Route]):
    model = Route

    def get_for_user(self, user: User, route_id: str) -> Route | None:
        query = self._owned_by(user).where(Route.id == route_id)
        return self._db.execute(query).scalar_one_or_none()

    def list_for_user(self, user: User, limit: int, offset: int) -> list[Route]:
        query = self._owned_by(user).order_by(Route.created_at.desc(), Route.id).limit(limit).offset(offset)
        return list(self._db.execute(query).scalars().all())

    def list_tracking_targets(self, today: date) -> list[tuple[str, str]]:
        query = (
            select(Route.id, Route.user_id)
            .where(Route.is_active.is_(True), Route.departure_date >= today)
            .order_by(Route.departure_date.asc())
        )
        rows = self._db.execute(query).all()

        return [(str(route_id), str(user_id)) for route_id, user_id in rows]

    def _owned_by(self, user: User) -> Select[Route]:
        """Routes that belong to the given user."""
        return select(Route).where(Route.user_id == user.id)
