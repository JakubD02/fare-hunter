from datetime import date

from sqlalchemy import Select, func, select

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

    def count_for_user(self, user_id: str) -> int:
        stmt = select(func.count()).select_from(Route).where(Route.user_id == user_id)
        return self._db.execute(stmt).scalar_one()

    def exists_for_pair(self, user_id: str, origin_id: str, destination_id: str) -> bool:
        stmt = (
            select(Route.id)
            .where(
                Route.user_id == user_id,
                Route.origin_id == origin_id,
                Route.destination_id == destination_id,
            )
            .limit(1)
        )
        return self._db.execute(stmt).first() is not None

    def _owned_by(self, user: User) -> Select[Route]:
        """Routes that belong to the given user."""
        return select(Route).where(Route.user_id == user.id)
