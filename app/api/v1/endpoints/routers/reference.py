from fastapi import APIRouter

from app.api.v1.dependencies import PaginationDep, ReferenceServiceDep
from app.api.v1.schemas.airline import AirlineRead
from app.api.v1.schemas.airport import AirportRead

router = APIRouter(tags=["reference"])


@router.get("/airports", response_model=list[AirportRead])
def list_airports(service: ReferenceServiceDep, page: PaginationDep):
    return service.list_airports(limit=page.limit, offset=page.offset)


@router.get("/airlines", response_model=list[AirlineRead])
def list_airlines(service: ReferenceServiceDep, page: PaginationDep):
    return service.list_airlines(limit=page.limit, offset=page.offset)
