from app.api.v1.schemas.price_alert import PriceAlertCreate, PriceAlertUpdate
from app.models.price_alert import PriceAlert
from app.models.user import User
from app.repositories.alert_repository import AlertRepository
from app.services.route_service import RouteService


class AlertService:
    def __init__(self, alerts: AlertRepository, routes: RouteService) -> None:
        self._alerts = alerts
        self._routes = routes

    def get_alert(self, user: User, route_id: str) -> PriceAlert | None:
        return self._alerts.get_for_route(user, route_id)

    def upsert_alert(self, user: User, route_id: str, alert_in: PriceAlertUpdate) -> PriceAlert | None:
        if self._routes.get_route(user, route_id) is None:
            return None

        data = alert_in.model_dump(exclude_unset=True)

        if "threshold_price" in data and data["threshold_price"] is None:
            raise ValueError("threshold_price cannot be null")

        alert = self._alerts.get_for_route(user, route_id)

        if alert is not None:
            for field, value in data.items():
                setattr(alert, field, value)
            return self._alerts.save(alert)

        if "threshold_price" not in data:
            raise ValueError("threshold_price is required to create an alert")

        create_in = PriceAlertCreate(route_id=route_id, **data)
        return self._alerts.add(PriceAlert(**create_in.model_dump()))

    def remove_alert(self, user: User, route_id: str) -> bool:
        alert = self._alerts.get_for_route(user, route_id)
        if alert is None:
            return False

        self._alerts.delete(alert)
        return True
