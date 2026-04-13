import uuid

from app.modules.bookings.events import BookingCreatedEvent
from app.modules.bookings.models import Booking
from app.modules.bookings.repository import BookingRepository
from app.shared.event_bus import event_bus


class BookingService:
    def __init__(self, repository: BookingRepository):
        self.repository = repository

    def get_all(self) -> list[Booking]:
        return self.repository.get_all()

    def get_by_id(self, booking_id: uuid.UUID) -> Booking | None:
        return self.repository.get_by_id(booking_id)

    def get_by_trip_id(self, trip_id: uuid.UUID) -> list[Booking]:
        return self.repository.get_by_trip_id(trip_id)

    def create(self, booking: Booking) -> Booking:
        # Persist the booking
        created_booking = self.repository.create(booking)

        # Publish the event
        event = BookingCreatedEvent(
            booking_id=created_booking.id,
            trip_id=created_booking.trip_id,
            parent_name=created_booking.parent_name,
            child_name=created_booking.child_name,
        )
        event_bus.publish(event)

        return created_booking
