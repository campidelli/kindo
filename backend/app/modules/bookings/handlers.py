import logging

from app.modules.bookings.events import (
    BookingCancelledEvent,
    BookingConfirmedEvent,
    BookingCreatedEvent,
    BookingFailedEvent,
)
from app.modules.bookings.service import BookingService
from app.modules.payments.events import PaymentSucceededEvent, PaymentFailedEvent
from app.shared.event_bus import get_event_bus

logger = logging.getLogger(__name__)


class BookingEventHandlers:
    def __init__(self, booking_service: BookingService):
        self.booking_service = booking_service

    def handle_booking_created(self, event: BookingCreatedEvent) -> None:
        """Handler for BookingCreatedEvent"""
        logger.info(
            f"Booking created: booking_id={event.booking_id}, trip_id={event.trip_id}, parent_name={event.parent_name}, child_name={event.child_name}"
        )
        # TODO: send welcome email

    def handle_booking_cancelled(self, event: BookingCancelledEvent) -> None:
        """Handler for BookingCancelledEvent"""
        logger.info(
            f"Booking cancelled: booking_id={event.booking_id}, trip_id={event.trip_id}, parent_name={event.parent_name}, child_name={event.child_name}"
        )
        # TODO: send cancellation email

    def handle_booking_confirmed(self, event: BookingConfirmedEvent) -> None:
        """Handler for BookingConfirmedEvent"""
        logger.info(
            f"Booking confirmed: booking_id={event.booking_id}, trip_id={event.trip_id}, parent_name={event.parent_name}, child_name={event.child_name}"
        )
        # TODO: send confirmation email

    def handle_booking_failed(self, event: BookingFailedEvent) -> None:
        """Handler for BookingFailedEvent"""
        logger.info(
            f"Booking failed: booking_id={event.booking_id}, trip_id={event.trip_id}, parent_name={event.parent_name}, child_name={event.child_name}"
        )
        # TODO: send failure email

    def handle_payment_succeeded(self, event: PaymentSucceededEvent) -> None:
        """Handler for PaymentSucceededEvent - confirms the booking"""
        logger.info(f"Payment succeeded for booking_id={event.booking_id}, confirming booking")
        self.booking_service.confirm(event.booking_id)

    def handle_payment_failed(self, event: PaymentFailedEvent) -> None:
        """Handler for PaymentFailedEvent - marks the booking as failed"""
        logger.info(f"Payment failed for booking_id={event.booking_id}, marking booking as failed")
        self.booking_service.fail(event.booking_id)

    def register_handlers(self) -> None:
        """Register all event handlers"""
        bus = get_event_bus()
        bus.subscribe(BookingCreatedEvent, self.handle_booking_created)
        bus.subscribe(BookingCancelledEvent, self.handle_booking_cancelled)
        bus.subscribe(BookingConfirmedEvent, self.handle_booking_confirmed)
        bus.subscribe(BookingFailedEvent, self.handle_booking_failed)
        bus.subscribe(PaymentSucceededEvent, self.handle_payment_completed)
        bus.subscribe(PaymentFailedEvent, self.handle_payment_failed)
