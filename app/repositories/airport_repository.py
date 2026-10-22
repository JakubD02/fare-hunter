from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.airport import Airport


class AirportRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_by_id(self, airport_id: str) -> Airport | None:
        return self._db.get(Airport, airport_id)

    def list_all(self, limit: int, offset: int) -> list[Airport]:
        stmt = select(Airport).order_by(Airport.iata_code).limit(limit).offset(offset)
        return list(self._db.execute(stmt).scalars())
