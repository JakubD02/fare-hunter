from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.api.auth import CurrentUser
from app.api.v1.dependencies import PaginationDep
from app.api.v1.schemas.route import RouteCreate, RouteRead, RouteUpdate
from app.core.database import get_db
from app.repositories.airport_repository import AirportRepository
from app.repositories.route_repository import RouteRepository
from app.services.route_service import RouteService
from app.tasks.price_tasks import fetch_prices_for_route

router = APIRouter(prefix="/routes", tags=["routes"])

db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/", response_model=list[RouteRead])
def list_routes(db: db_dependency, current_user: CurrentUser, page: PaginationDep):
    service = RouteService(routes=RouteRepository(db), airports=AirportRepository(db))
    return service.list_routes(user=current_user, limit=page.limit, offset=page.offset)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=RouteRead)
def create_route(db: db_dependency, current_user: CurrentUser, route_in: RouteCreate):
    service = RouteService(routes=RouteRepository(db), airports=AirportRepository(db))
    try:
        route = service.create_route(user=current_user, route_in=route_in)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

    fetch_prices_for_route.delay(route_id=route.id, user_id=str(current_user.id))

    return route


@router.get("/{route_id}", response_model=RouteRead)
def get_route(db: db_dependency, current_user: CurrentUser, route_id: str):
    service = RouteService(routes=RouteRepository(db), airports=AirportRepository(db))
    route = service.get_route(user=current_user, route_id=route_id)

    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found.")

    return route


@router.patch("/{route_id}", response_model=RouteRead)
def update_route(db: db_dependency, current_user: CurrentUser, route_in: RouteUpdate, route_id: str):
    service = RouteService(routes=RouteRepository(db), airports=AirportRepository(db))
    route = service.update_route(user=current_user, route_id=route_id, route_in=route_in)

    if not route:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found.")

    return route


@router.delete(
    "/{route_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_route(db: db_dependency, current_user: CurrentUser, route_id: str) -> None:
    service = RouteService(routes=RouteRepository(db), airports=AirportRepository(db))
    removed = service.remove_route(user=current_user, route_id=route_id)

    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found.")
