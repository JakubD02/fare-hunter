from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import CurrentUser
from app.database import get_db
from app.schemas.route import RouteCreate, RouteRead, RouteUpdate
from app.services import routes_service as rs

router = APIRouter(prefix="/routes", tags=["routes"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/")
async def list_routes(db: db_dependency, current_user: CurrentUser):
    return rs.list_routes(db, user=current_user)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RouteRead)
async def create_route(
    db: db_dependency, current_user: CurrentUser, route_in: RouteCreate
):
    route = rs.create_route(db=db, user=current_user, route_in=route_in)

    return route


@router.get("/{route_id}", response_model=RouteRead)
async def get_route(db: db_dependency, current_user: CurrentUser, route_id: int):
    return rs.get_route(db=db, user=current_user, route_id=route_id)


@router.patch("/{route_id}", response_model=RouteRead)
async def update_route(
    db: db_dependency, current_user: CurrentUser, route_in: RouteUpdate, route_id: int
):
    route = rs.update_route(
        db=db, user=current_user, route_id=route_id, route_in=route_in
    )

    if not route:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found."
        )

    return route


@router.delete("/{route_id}")
async def remove_route(
    db: db_dependency, current_user: CurrentUser, route_id: int
) -> None:
    deleted = rs.remove_route(db=db, user=current_user, route_id=route_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Route not found."
        )
