from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import engine
from app.models import Airline, Airport
from scripts.data import AIRLINES_DATA, AIRPORTS_DATA


def seed_airports(db: Session):
    if db.execute(select(Airline)).scalars().first():
        print("Airports already seeded, skipping")
        return

    airports = [Airport(**data) for data in AIRPORTS_DATA]
    db.add_all(airports)
    db.commit()


def seed_airlines(db: Session):
    if db.execute(select(Airline)).scalars().first():
        print("Airlines already seeded, skipping")
        return

    airlines = [Airline(**data) for data in AIRLINES_DATA]
    db.add_all(airlines)
    db.commit()


def seed_data() -> None:
    with Session(engine) as session:
        seed_airports(session)
        seed_airlines(session)


if __name__ == "__main__":
    seed_data()
