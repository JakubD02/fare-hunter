from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.price_alert import PriceAlert
from app.models.route import Route
from app.models.user import User
from app.schemas.price_alert import PriceAlertCreate, PriceAlertUpdate
from app.services import route_service


def get_alert(db: Session, user: User, route_id: str) -> PriceAlert | None:
    query = (
        select(PriceAlert)
        .join(Route, PriceAlert.route_id == Route.id)
        .where(
            Route.id == route_id,
            Route.user_id == user.id,
        )
    )

    return db.execute(query).scalar_one_or_none()


def upsert_alert(db: Session, user: User, route_id: str, alert_in: PriceAlertUpdate) -> PriceAlert | None:
    route = route_service.get_route(db=db, user=user, route_id=route_id)
    if not route:
        return None

    alert = get_alert(db=db, user=user, route_id=route_id)
    data = alert_in.model_dump(exclude_unset=True)

    if alert:
        # Update existing alert
        for field, value in data.items():
            setattr(alert, field, value)
    else:
        # Create new alert
        try:
            create_in = PriceAlertCreate(route_id=route_id, **data)
            alert = PriceAlert(**create_in.model_dump())
        except ValueError:
            return None

    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def remove_alert(db: Session, user: User, route_id: str) -> bool:
    alert = get_alert(db=db, user=user, route_id=route_id)
    if not alert:
        return False

    db.delete(alert)
    db.commit()
    return True
