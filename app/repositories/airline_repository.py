from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.airline import Airline


class AirlineRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def find_id(self, airline_name: str | None) -> str | None:
        """Resolve an airline by IATA code or name, case-insensitively."""
        if not airline_name:
            return None

        needle = airline_name.strip().lower()
        if not needle:
            return None

        stmt = select(Airline.id).where(
            (func.lower(Airline.iata_code) == needle) | (func.lower(Airline.name) == needle)
        )
        return self._db.execute(stmt).scalar_one_or_none()

    def list_all(self) -> list[Airline]:
        query = select(Airline).order_by(Airline.name)
        return list(self._db.scalars(query).all())
