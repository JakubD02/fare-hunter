import logging

from app.api.v1.schemas.price_alert import PriceAlertCreate, PriceAlertUpdate
from app.models.price_alert import PriceAlert
from app.models.user import User
from app.repositories.alert_repository import AlertRepository
from app.services.route_service import RouteService

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self, alerts: AlertRepository, routes: RouteService) -> None:
        self._alerts = alerts
        self._routes = routes

    def get_alert(self, user: User, route_id: str) -> PriceAlert | None:
        alert = self._alerts.get_for_route(user, route_id)
        logger.debug("alert lookup route_id=%s user_id=%s found=%s", route_id, user.id, alert is not None)
        return alert

    def upsert_alert(self, user: User, route_id: str, alert_in: PriceAlertUpdate) -> PriceAlert | None:
        if self._routes.get_route(user, route_id) is None:
            logger.warning("alert upsert rejected: route not found route_id=%s user_id=%s", route_id, user.id)
            return None

        data = alert_in.model_dump(exclude_unset=True)

        if "threshold_price" in data and data["threshold_price"] is None:
            logger.warning("alert upsert rejected: null threshold route_id=%s user_id=%s", route_id, user.id)
            raise ValueError("threshold_price cannot be null")

        alert = self._alerts.get_for_route(user, route_id)

        if alert is not None:
            for field, value in data.items():
                setattr(alert, field, value)
            alert = self._alerts.save(alert)
            logger.info(
                "alert updated id=%s route_id=%s user_id=%s fields=%s",
                alert.id,
                route_id,
                user.id,
                sorted(data.keys()),
            )
            return alert

        if "threshold_price" not in data:
            logger.warning("alert create rejected: threshold missing route_id=%s user_id=%s", route_id, user.id)
            raise ValueError("threshold_price is required to create an alert")

        create_in = PriceAlertCreate(route_id=route_id, **data)
        alert = self._alerts.add(PriceAlert(**create_in.model_dump()))
        logger.info(
            "alert created id=%s route_id=%s user_id=%s threshold=%s",
            alert.id,
            route_id,
            user.id,
            alert.threshold_price,
        )
        return alert

    def remove_alert(self, user: User, route_id: str) -> bool:
        alert = self._alerts.get_for_route(user, route_id)
        if alert is None:
            return False

        self._alerts.delete(alert)
        logger.info("alert removed id=%s route_id=%s user_id=%s", alert.id, route_id, user.id)
        return True
