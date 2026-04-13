from unittest.mock import MagicMock

from app.modules.bookings.events import (
    BookingCancelledEvent,
    BookingConfirmedEvent,
    BookingCreatedEvent,
    BookingFailedEvent,
)
from app.modules.bookings.models import BookingStatus
from app.modules.bookings.service import BookingService
from tests.conftest import make_booking


def make_service(repository: MagicMock, event_bus: MagicMock) -> BookingService:
    return BookingService(repository, event_bus)


class TestBookingService:
    def test_create_persists_booking_and_publishes_created_event(self):
        booking = make_booking()
        repository = MagicMock()
        repository.create.return_value = booking
        event_bus = MagicMock()

        result = make_service(repository, event_bus).create(booking)

        assert result == booking
        repository.create.assert_called_once_with(booking)
        published_event = event_bus.publish.call_args.args[0]
        assert isinstance(published_event, BookingCreatedEvent)
        assert published_event.booking_id == booking.id
        assert published_event.trip_id == booking.trip_id

    def test_cancel_publishes_cancelled_event_when_booking_exists(self):
        booking = make_booking(status=BookingStatus.CANCELLED)
        repository = MagicMock()
        repository.cancel.return_value = booking
        event_bus = MagicMock()

        result = make_service(repository, event_bus).cancel(booking.id)

        assert result == booking
        repository.cancel.assert_called_once_with(booking.id)
        published_event = event_bus.publish.call_args.args[0]
        assert isinstance(published_event, BookingCancelledEvent)

    def test_cancel_does_not_publish_when_booking_missing(self):
        repository = MagicMock()
        repository.cancel.return_value = None
        event_bus = MagicMock()

        result = make_service(repository, event_bus).cancel(make_booking().id)

        assert result is None
        event_bus.publish.assert_not_called()

    def test_confirm_updates_status_and_publishes_confirmed_event(self):
        booking = make_booking(status=BookingStatus.CONFIRMED)
        repository = MagicMock()
        repository.update_status.return_value = booking
        event_bus = MagicMock()

        result = make_service(repository, event_bus).confirm(booking.id)

        assert result == booking
        repository.update_status.assert_called_once_with(booking.id, BookingStatus.CONFIRMED)
        published_event = event_bus.publish.call_args.args[0]
        assert isinstance(published_event, BookingConfirmedEvent)

    def test_fail_updates_status_and_publishes_failed_event(self):
        booking = make_booking(status=BookingStatus.FAILED)
        repository = MagicMock()
        repository.update_status.return_value = booking
        event_bus = MagicMock()

        result = make_service(repository, event_bus).fail(booking.id)

        assert result == booking
        repository.update_status.assert_called_once_with(booking.id, BookingStatus.FAILED)
        published_event = event_bus.publish.call_args.args[0]
        assert isinstance(published_event, BookingFailedEvent)