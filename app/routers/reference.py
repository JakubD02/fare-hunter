from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import reference_service

router = APIRouter(tags=["reference"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/airports")
async def list_airports(db: db_dependency):
    return reference_service.list_airports(db)


@router.get("/airlines")
async def list_airlines(db: db_dependency):
    return reference_service.list_airlines(db)
