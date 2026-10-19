from app.models.airline import Airline
from app.models.airport import Airport
from app.repositories.airline_repository import AirlineRepository
from app.repositories.airport_repository import AirportRepository


class ReferenceService:
    def __init__(self, airports: AirportRepository, airlines: AirlineRepository) -> None:
        self._airports = airports
        self._airlines = airlines

    def list_airports(self) -> list[Airport]:
        return self._airports.list_all()

    def get_airport(self, airport_id: str) -> Airport:
        airport_id = airport_id.strip()
        if not airport_id:
            raise LookupError("Airport ID cannot be empty")

        airport = self._airports.get_by_id(airport_id)
        if airport is None:
            raise LookupError(f"Airport with ID {airport_id} not found")
        return airport

    def list_airlines(self) -> list[Airline]:
        return self._airlines.list_all()

    def find_airline_id(self, airline_name: str | None) -> str | None:
        if not airline_name:
            return None

        needle = airline_name.strip()
        if not needle:
            return None

        return self._airlines.find_id(needle)
