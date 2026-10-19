from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.v1.schemas.airline import AirlineRead
from app.api.v1.schemas.airport import AirportRead
from app.core.database import get_db
from app.repositories.airline_repository import AirlineRepository
from app.repositories.airport_repository import AirportRepository
from app.services.reference_service import ReferenceService

router = APIRouter(tags=["reference"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/airports", response_model=list[AirportRead])
def list_airports(db: db_dependency):
    service = ReferenceService(airports=AirportRepository(db), airlines=AirlineRepository(db))
    return service.list_airports()


@router.get("/airlines", response_model=list[AirlineRead])
def list_airlines(db: db_dependency):
    service = ReferenceService(airports=AirportRepository(db), airlines=AirlineRepository(db))
    return service.list_airlines()
