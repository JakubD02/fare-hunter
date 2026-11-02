import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import engine
from app.models import Airline, Airport
from data import AIRLINES_DATA, AIRPORTS_DATA

logger = logging.getLogger(__name__)


def seed_airports(db: Session) -> None:
    existing = set(db.scalars(select(Airport.iata_code)))
    new = [Airport(**data) for data in AIRPORTS_DATA if data["iata_code"] not in existing]
    if not new:
        logger.debug("Airports up to date, nothing to seed")
        return
    db.add_all(new)
    db.commit()
    logger.info("Seeded %d new airports", len(new))


def seed_airlines(db: Session) -> None:
    existing = set(db.scalars(select(Airline.iata_code)))
    new = [Airline(**data) for data in AIRLINES_DATA if data["iata_code"] not in existing]
    if not new:
        logger.debug("Airlines up to date, nothing to seed")
        return
    db.add_all(new)
    db.commit()
    logger.info("Seeded %d new airlines", len(new))


def seed_data() -> None:
    with Session(engine) as session:
        seed_airports(session)
        seed_airlines(session)


if __name__ == "__main__":
    seed_data()
