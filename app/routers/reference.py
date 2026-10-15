from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.airline import AirlineRead
from app.schemas.airport import AirportRead
from app.services import reference_service

router = APIRouter(tags=["reference"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/airports", response_model=list[AirportRead])
def list_airports(db: db_dependency):
    return reference_service.list_airports(db)


@router.get("/airlines", response_model=list[AirlineRead])
def list_airlines(db: db_dependency):
    return reference_service.list_airlines(db)
