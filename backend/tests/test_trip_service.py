import uuid
from unittest.mock import MagicMock

from app.modules.trips.service import TripService
from tests.conftest import make_trip


def make_service(repository: MagicMock) -> TripService:
    return TripService(repository)


class TestTripService:
    def test_get_all_returns_all_trips(self):
        trips = [make_trip(), make_trip()]
        repository = MagicMock()
        repository.get_all.return_value = trips

        result = make_service(repository).get_all()

        assert result == trips
        repository.get_all.assert_called_once_with()

    def test_get_by_id_returns_trip_when_found(self):
        trip = make_trip()
        repository = MagicMock()
        repository.get_by_id.return_value = trip

        result = make_service(repository).get_by_id(trip.id)

        assert result == trip
        repository.get_by_id.assert_called_once_with(trip.id)

    def test_get_by_id_returns_none_when_not_found(self):
        repository = MagicMock()
        repository.get_by_id.return_value = None

        result = make_service(repository).get_by_id(uuid.uuid4())

        assert result is None
