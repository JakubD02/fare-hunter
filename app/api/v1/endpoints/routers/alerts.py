from fastapi import APIRouter, HTTPException
from starlette import status

from app.api.auth import CurrentUser
from app.api.v1.dependencies import AlertServiceDep
from app.api.v1.schemas.price_alert import PriceAlertRead, PriceAlertUpdate
from app.tasks.email_tasks import send_alert_confirmation_email_task

router = APIRouter(prefix="/routes", tags=["alerts"])


@router.get("/{route_id}/alert", response_model=PriceAlertRead)
def get_alert(service: AlertServiceDep, user: CurrentUser, route_id: str):
    alert = service.get_alert(user, route_id)

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No alert configured for this route",
        )
    return alert


@router.put("/{route_id}/alert", response_model=PriceAlertRead)
def upsert_alert(user: CurrentUser, route_id: str, alert_in: PriceAlertUpdate, service: AlertServiceDep):
    try:
        existed = service.get_alert(user, route_id) is not None
        alert = service.upsert_alert(user, route_id, alert_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e)) from e

    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")

    send_alert_confirmation_email_task.delay(
        route_id=route_id,
        user_id=str(user.id),
        action="updated" if existed else "created",
    )

    return alert


@router.delete("/{route_id}/alert", status_code=status.HTTP_204_NO_CONTENT)
def remove_alert(service: AlertServiceDep, user: CurrentUser, route_id: str) -> None:
    if not service.remove_alert(user, route_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found.")
