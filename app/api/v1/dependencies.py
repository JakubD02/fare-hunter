from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query

from app.core.config import settings


@dataclass(frozen=True)
class Pagination:
    limit: int
    offset: int


def get_pagination(
    limit: int = Query(
        default=settings.pagination.default_limit,
        ge=settings.pagination.min_limit,
        le=settings.pagination.max_limit,
    ),
    offset: int = Query(
        default=settings.pagination.default_offset,
        ge=settings.pagination.min_offset,
    ),
) -> Pagination:
    return Pagination(limit=limit, offset=offset)


PaginationDep = Annotated[Pagination, Depends(get_pagination)]
