import logging

from app.models.airline import Airline
from app.models.airport import Airport
from app.repositories.airline_repository import AirlineRepository
from app.repositories.airport_repository import AirportRepository

logger = logging.getLogger(__name__)


class ReferenceService:
    def __init__(self, airports: AirportRepository, airlines: AirlineRepository) -> None:
        self._airports = airports
        self._airlines = airlines

    def list_airports(self, limit: int, offset: int) -> list[Airport]:
        airports = self._airports.list_all(limit=limit, offset=offset)
        logger.debug("airports listed count=%d limit=%d offset=%d", len(airports), limit, offset)
        return airports

    def get_airport(self, airport_id: str) -> Airport:
        airport_id = airport_id.strip()
        if not airport_id:
            logger.warning("airport lookup rejected: empty id")
            raise LookupError("Airport ID cannot be empty")

        airport = self._airports.get_by_id(airport_id)
        if airport is None:
            logger.warning("airport not found id=%s", airport_id)
            raise LookupError(f"Airport with ID {airport_id} not found")
        return airport

    def list_airlines(self, limit: int, offset: int) -> list[Airline]:
        airlines = self._airlines.list_all(limit=limit, offset=offset)
        logger.debug("airlines listed count=%d limit=%d offset=%d", len(airlines), limit, offset)
        return airlines

    def find_airline_id(self, airline_name: str | None) -> str | None:
        if not airline_name:
            return None

        needle = airline_name.strip()
        if not needle:
            return None

        airline_id = self._airlines.find_id(needle)
        logger.debug("airline resolved needle=%s found=%s", needle, airline_id is not None)
        return airline_id
