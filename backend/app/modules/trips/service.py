import uuid

from app.modules.trips.models import Trip
from app.modules.trips.repository import TripRepository


class TripService:
    def __init__(self, repository: TripRepository):
        self.repository = repository

    def get_all(self) -> list[Trip]:
        return self.repository.get_all()

    def get_by_id(self, trip_id: uuid.UUID) -> Trip | None:
        return self.repository.get_by_id(trip_id)
