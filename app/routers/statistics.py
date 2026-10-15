from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import CurrentUser
from app.database import get_db
from app.schemas.flight_price import FlightPriceRead, FlightStats
from app.services import flight_price_service

router = APIRouter(prefix="/routes", tags=["statistics"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/{route_id}/stats", response_model=FlightStats)
def get_stats(db: db_dependency, current_user: CurrentUser, route_id: str) -> FlightStats:
    stats = flight_price_service.get_stats(db=db, user=current_user, route_id=route_id)
    if stats is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )
    return FlightStats.model_validate(stats)


@router.get("/{route_id}/history", response_model=list[FlightPriceRead])
def get_history(db: db_dependency, current_user: CurrentUser, route_id: str) -> list[FlightPriceRead]:
    history = flight_price_service.get_history(db=db, user=current_user, route_id=route_id)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found",
        )

    return [FlightPriceRead.model_validate(item) for item in history]
