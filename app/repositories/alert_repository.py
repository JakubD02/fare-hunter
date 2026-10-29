from sqlalchemy import Select, select

from app.models.price_alert import PriceAlert
from app.models.route import Route
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class AlertRepository(BaseRepository[PriceAlert]):
    model = PriceAlert

    def get_for_route(self, user: User, route_id: str) -> PriceAlert | None:
        query = self._owned_by(user).where(PriceAlert.route_id == route_id)
        return self._db.execute(query).scalar_one_or_none()

    def get_route_by_id(self, user: User, alert_id: str) -> PriceAlert | None:
        query = (
            select(PriceAlert)
            .join(Route, PriceAlert.route_id == Route.id)
            .where(PriceAlert.id == alert_id, Route.user_id == user.id)
        )
        return self._db.scalar(query)

    def get_active_by_route_id(self, route_id: str) -> PriceAlert | None:
        query = select(PriceAlert).where(
            PriceAlert.route_id == route_id,
            PriceAlert.is_active.is_(True),
        )
        return self._db.execute(query).scalar_one_or_none()

    def _owned_by(self, user: User) -> Select[PriceAlert]:
        """Alerts on routes that belong to the given user."""
        return select(PriceAlert).join(Route, PriceAlert.route_id == Route.id).where(Route.user_id == user.id)
