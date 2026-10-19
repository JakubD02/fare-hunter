from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.api.auth import CurrentUser
from app.api.v1.schemas.price_alert import PriceAlertRead, PriceAlertUpdate
from app.core.database import get_db
from app.repositories.airport_repository import AirportRepository
from app.repositories.alert_repository import AlertRepository
from app.repositories.route_repository import RouteRepository
from app.services.alert_service import AlertService
from app.services.route_service import RouteService

# from app.tasks.email_tasks import send_alert_confirmation_email_task

router = APIRouter(prefix="/routes", tags=["alerts"])

db_dependency = Annotated[Session, Depends(get_db)]


def _alert_service(db: Session) -> AlertService:
    routes = RouteService(
        routes=RouteRepository(db),
        airports=AirportRepository(db),
    )
    return AlertService(alerts=AlertRepository(db), routes=routes)


@router.get("/{route_id}/alert", response_model=PriceAlertRead)
def get_alert(db: db_dependency, user: CurrentUser, route_id: str):
    alert = _alert_service(db).get_alert(user, route_id)

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No alert configured for this route",
        )
    return alert


@router.put("/{route_id}/alert", response_model=PriceAlertRead)
def upsert_alert(
    db: db_dependency,
    user: CurrentUser,
    route_id: str,
    alert_in: PriceAlertUpdate,
):
    try:
        alert = _alert_service(db).upsert_alert(user, route_id, alert_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    # send_alert_confirmation_email_task.delay(
    #     user_id=str(user.id),
    #     alert_id=alert.id,
    # )

    return alert


@router.delete("/{route_id}/alert", status_code=status.HTTP_204_NO_CONTENT)
def remove_alert(db: db_dependency, user: CurrentUser, route_id: str) -> None:
    if not _alert_service(db).remove_alert(user, route_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
