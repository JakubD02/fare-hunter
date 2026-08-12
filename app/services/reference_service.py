from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.airline import Airline
from app.models.airport import Airport


def get_all_airports(db: Session) -> list[Airport]:
    query = select(
        Airport.name, Airport.city, Airport.country, Airport.country_code
    ).order_by(Airport.name)

    return list(db.execute(query).all())


def get_all_airlines(db: Session) -> list[Airline]:
    query = select(Airline.name).order_by(Airline.name)

    return list(db.execute(query).all())
