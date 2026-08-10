from app.database import SessionLocal
from app.models import Airline, Airport
from scripts.data.airlines import AIRLINES_DATA
from scripts.data.airports import AIRPORTS_DATA


def seed_airports(db):
    if db.query(Airport).first():
        print("Airports already seeded, skipping")
        return

    airports = [Airport(**data) for data in AIRPORTS_DATA]
    db.add_all(airports)
    db.commit()


def seed_airlines(db):
    if db.query(Airline).first():
        print("Airlines already seeded, skipping")
        return

    airlines = [Airline(**data) for data in AIRLINES_DATA]
    db.add_all(airlines)
    db.commit()


def main():
    """Main function - creates session, calls seed functions."""
    db = SessionLocal()
    try:
        seed_airports(db)
        seed_airlines(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
