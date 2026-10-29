from app.models.airport import Airport
from app.repositories.base_repository import BaseRepository


class AirportRepository(BaseRepository[Airport]):
    model = Airport
