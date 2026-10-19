from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.price_alert import PriceAlert
from app.models.route import Route
from app.models.user import User


class AlertRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_for_route(self, user: User, route_id: str) -> PriceAlert | None:
        query = (
            select(PriceAlert)
            .join(Route, PriceAlert.route_id == Route.id)
            .where(Route.id == route_id, Route.user_id == user.id)
        )
        return self._db.execute(query).scalar_one_or_none()

    def add(self, alert: PriceAlert) -> PriceAlert:
        self._db.add(alert)
        self._db.commit()
        self._db.refresh(alert)
        return alert

    def save(self, alert: PriceAlert) -> PriceAlert:
        self._db.commit()
        self._db.refresh(alert)
        return alert

    def delete(self, alert: PriceAlert) -> None:
        self._db.delete(alert)
        self._db.commit()
