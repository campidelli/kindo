import uuid

from app.modules.bookings.events import (
    BookingCancelledEvent,
    BookingConfirmedEvent,
    BookingCreatedEvent,
    BookingFailedEvent,
)
from app.modules.bookings.models import Booking, BookingStatus
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

    def cancel(self, booking_id: uuid.UUID) -> Booking | None:
        cancelled_booking = self.repository.cancel(booking_id)
        
        if cancelled_booking:
            # Publish the event
            event = BookingCancelledEvent(
                booking_id=cancelled_booking.id,
                trip_id=cancelled_booking.trip_id,
                parent_name=cancelled_booking.parent_name,
                child_name=cancelled_booking.child_name,
            )
            event_bus.publish(event)
        
        return cancelled_booking

    def confirm(self, booking_id: uuid.UUID) -> Booking | None:
        confirmed_booking = self.repository.update_status(booking_id, BookingStatus.CONFIRMED)
        if confirmed_booking:
            event_bus.publish(
                BookingConfirmedEvent(
                    booking_id=confirmed_booking.id,
                    trip_id=confirmed_booking.trip_id,
                    parent_name=confirmed_booking.parent_name,
                    child_name=confirmed_booking.child_name,
                )
            )
        return confirmed_booking

    def fail(self, booking_id: uuid.UUID) -> Booking | None:
        failed_booking = self.repository.update_status(booking_id, BookingStatus.FAILED)
        if failed_booking:
            event_bus.publish(
                BookingFailedEvent(
                    booking_id=failed_booking.id,
                    trip_id=failed_booking.trip_id,
                    parent_name=failed_booking.parent_name,
                    child_name=failed_booking.child_name,
                )
            )
        return failed_booking
