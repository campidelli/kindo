import uuid
from unittest.mock import MagicMock

import pytest

from app.services.trip_service import TripService
from tests.conftest import make_trip, mock_session


def make_service(trip_repo: MagicMock) -> TripService:
    service = TripService.__new__(TripService)
    service.repository = trip_repo
    return service


class TestGetAll:
    def test_returns_all_trips(self):
        trips = [make_trip(), make_trip()]
        repo = MagicMock()
        repo.get_all.return_value = trips

        result = make_service(repo).get_all()

        assert result == trips
        repo.get_all.assert_called_once()

    def test_returns_empty_list_when_no_trips(self):
        repo = MagicMock()
        repo.get_all.return_value = []

        result = make_service(repo).get_all()

        assert result == []


class TestGetById:
    def test_returns_trip_when_found(self):
        trip = make_trip()
        repo = MagicMock()
        repo.get_by_id.return_value = trip

        result = make_service(repo).get_by_id(trip.id)

        assert result == trip
        repo.get_by_id.assert_called_once_with(trip.id)

    def test_returns_none_when_not_found(self):
        repo = MagicMock()
        repo.get_by_id.return_value = None

        result = make_service(repo).get_by_id(uuid.uuid4())

        assert result is None
