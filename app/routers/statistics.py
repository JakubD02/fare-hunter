from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import CurrentUser
from app.database import get_db
from app.models.flight_price import FlightPrice
from app.schemas.flight_price import FlightPriceRead, FlightStats
from app.services import flight_price_service

router = APIRouter(prefix="/routes", tags=["statistics"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/{route_id}/stats", response_model=list[FlightPriceRead])
async def get_stats(
    db: db_dependency, current_user: CurrentUser, route_id: int
) -> dict | None:
    stats = flight_price_service.get_stats(db=db, user=current_user, route_id=route_id)

    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )
    return stats


@router.get("/{route_id}/history", response_model=FlightStats)
async def get_history(
    db: db_dependency, current_user: CurrentUser, route_id: int
) -> list[FlightPrice] | None:
    history = flight_price_service.get_history(
        db=db, user=current_user, route_id=route_id
    )

    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )
    return history
