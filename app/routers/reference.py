from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.reference_service import get_all_airports

router = APIRouter(tags=["reference"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/airports")
async def get_airports(db: db_dependency):
    return get_all_airports(db)


@router.get("/airlines")
async def get_airlines(db: db_dependency):
    return get_airlines(db)
