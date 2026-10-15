from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.airline import Airline
from app.models.airport import Airport


def find_airline_id(db: Session, airline_name: str | None) -> str | None:
    """Resolve an airline by IATA code or name, case-insensitively."""
    if not airline_name:
        return None

    needle = airline_name.strip().lower()
    if not needle:
        return None

    stmt = select(Airline.id).where((func.lower(Airline.iata_code) == needle) | (func.lower(Airline.name) == needle))
    return db.execute(stmt).scalar_one_or_none()


def list_airports(db: Session) -> list[Airport]:
    query = select(Airport).order_by(Airport.name)

    return list(db.scalars(query).all())


def list_airlines(db: Session) -> list[Airline]:
    query = select(Airline).order_by(Airline.name)

    return list(db.scalars(query).all())
