from sqlalchemy import func, select

from app.models.airline import Airline
from app.repositories.base_repository import BaseRepository


class AirlineRepository(BaseRepository[Airline]):
    model = Airline

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

    def list_all(self, limit: int, offset: int) -> list[Airline]:
        stmt = select(Airline).order_by(Airline.iata_code).limit(limit).offset(offset)
        return list(self._db.execute(stmt).scalars())
