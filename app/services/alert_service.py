from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.price_alert import PriceAlert
from app.models.route import Route
from app.models.user import User
from app.schemas.price_alert import PriceAlertUpdate
from app.services import routes_service


def get_alert(db: Session, user: User, route_id: int) -> PriceAlert | None:
    query = (
        select(PriceAlert)
        .join(Route, PriceAlert.route_id == Route.id)
        .where(
            Route.id == route_id,
            Route.user_id == user.id,
        )
    )

    return db.execute(query).scalar_one_or_none()


def upsert_alert(
    db: Session, user: User, route_id: int, alert_in: PriceAlertUpdate
) -> PriceAlert | None:
    route = routes_service.get_route(db=db, user=user, route_id=route_id)
    if not route:
        return None

    alert = get_alert(db=db, user=user, route_id=route_id)

    if alert:
        # Update existing alert
        data = alert_in.model_dump()
        for field, value in data.items():
            setattr(alert, field, value)
    else:
        # Create new alert
        alert = PriceAlert(
            route_id=route_id,
            threshold_price=alert_in.threshold_price,
            currency=alert_in.currency,
            is_active=alert_in.is_active,
        )
        db.add(alert)

    db.commit()
    db.refresh(alert)
    return alert


def remove_alert(db: Session, user: User, route_id: int) -> bool:
    alert = get_alert(db=db, user=user, route_id=route_id)
    if not alert:
        return False

    db.delete(alert)
    db.commit()
    return True
