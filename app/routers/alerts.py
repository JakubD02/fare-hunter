from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import CurrentUser
from app.database import get_db
from app.schemas.price_alert import PriceAlertCreate, PriceAlertRead
from app.services import alert_service

router = APIRouter(tags=["alerts"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/{route_id}/alert", response_model=PriceAlertRead)
async def get_alert(db: db_dependency, current_user: CurrentUser, route_id: int):
    alert = alert_service.get_alert(db=db, user=current_user, route_id=route_id)

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No alert configured for this route",
        )
    return alert


@router.put("/{route_id}/alert", response_model=PriceAlertRead)
async def upsert_alert(
    db: db_dependency,
    current_user: CurrentUser,
    route_id: int,
    alert_in: PriceAlertCreate,
):
    alert = alert_service.upsert_alert(
        db=db, user=current_user, route_id=route_id, alert_in=alert_in
    )

    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found."
        )

    return alert


@router.delete("/{route_id}/alert", status_code=status.HTTP_204_NO_CONTENT)
async def remove_alert(
    db: db_dependency, current_user: CurrentUser, route_id: int
) -> None:
    deleted = alert_service.remove_alert(db=db, user=current_user, route_id=route_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found."
        )
