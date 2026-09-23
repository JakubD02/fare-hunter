from sqlalchemy.orm import Session

from app.database import engine
from app.models.airline import Airline
from app.models.airport import Airport
from app.models.base import Base


def init_db():
    Base.metadata.create_all(engine)
    seed_data()


def seed_data():
    with Session(engine) as session:
        if session.query(Airport).first():
            return

        airports_data = [
            {
                "iata_code": "JFK",
                "name": "John F. Kennedy International",
                "city": "New York",
                "country": "United States",
                "country_code": "US",
            },
            {
                "iata_code": "LHR",
                "name": "London Heathrow",
                "city": "London",
                "country": "United Kingdom",
                "country_code": "GB",
            },
            {
                "iata_code": "CDG",
                "name": "Charles de Gaulle",
                "city": "Paris",
                "country": "France",
                "country_code": "FR",
            },
            {
                "iata_code": "AMS",
                "name": "Amsterdam Airport Schiphol",
                "city": "Amsterdam",
                "country": "Netherlands",
                "country_code": "NL",
            },
            {
                "iata_code": "DUB",
                "name": "Dublin Airport",
                "city": "Dublin",
                "country": "Ireland",
                "country_code": "IE",
            },
            {
                "iata_code": "WAW",
                "name": "Warsaw Chopin",
                "city": "Warsaw",
                "country": "Poland",
                "country_code": "PL",
            },
            {
                "iata_code": "WRO",
                "name": "Wrocław Nicolaus Copernicus",
                "city": "Wrocław",
                "country": "Poland",
                "country_code": "PL",
            },
            {
                "iata_code": "KRK",
                "name": "Kraków John Paul II",
                "city": "Kraków",
                "country": "Poland",
                "country_code": "PL",
            },
            {
                "iata_code": "LAX",
                "name": "Los Angeles International",
                "city": "Los Angeles",
                "country": "United States",
                "country_code": "US",
            },
            {
                "iata_code": "ORD",
                "name": "Chicago O'Hare",
                "city": "Chicago",
                "country": "United States",
                "country_code": "US",
            },
        ]

        airlines_data = [
            {"iata_code": "LO", "name": "LOT Polish Airlines"},
            {"iata_code": "BA", "name": "British Airways"},
            {"iata_code": "AF", "name": "Air France"},
            {"iata_code": "KL", "name": "KLM Royal Dutch Airlines"},
            {"iata_code": "EI", "name": "Aer Lingus"},
            {"iata_code": "UA", "name": "United Airlines"},
            {"iata_code": "AA", "name": "American Airlines"},
            {"iata_code": "LH", "name": "Lufthansa"},
        ]

        airports = [Airport(**data) for data in airports_data]
        airlines = [Airline(**data) for data in airlines_data]

        session.add_all(airports)
        session.add_all(airlines)
        session.commit()


if __name__ == "__main__":
    init_db()
