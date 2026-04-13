import logging
from collections.abc import Callable
from contextlib import AbstractContextManager

from app.modules.bookings.events import (
    BookingCancelledEvent,
    BookingConfirmedEvent,
    BookingCreatedEvent,
    BookingFailedEvent,
)
from app.modules.bookings.service import BookingService
from app.modules.payments.events import PaymentSucceededEvent, PaymentFailedEvent
from app.shared.event_bus import EventBus

logger = logging.getLogger(__name__)


class BookingEventHandlers:
    def __init__(
        self,
        booking_service_factory: Callable[[], AbstractContextManager[BookingService]],
        event_bus: EventBus,
    ):
        self.booking_service_factory = booking_service_factory
        self.event_bus = event_bus

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
        with self.booking_service_factory() as booking_service:
            booking_service.confirm(event.booking_id)

    def handle_payment_failed(self, event: PaymentFailedEvent) -> None:
        """Handler for PaymentFailedEvent - marks the booking as failed"""
        logger.info(f"Payment failed for booking_id={event.booking_id}, marking booking as failed")
        with self.booking_service_factory() as booking_service:
            booking_service.fail(event.booking_id)

    def register_handlers(self) -> None:
        """Register all event handlers"""
        self.event_bus.subscribe(BookingCreatedEvent, self.handle_booking_created)
        self.event_bus.subscribe(BookingCancelledEvent, self.handle_booking_cancelled)
        self.event_bus.subscribe(BookingConfirmedEvent, self.handle_booking_confirmed)
        self.event_bus.subscribe(BookingFailedEvent, self.handle_booking_failed)
        self.event_bus.subscribe(PaymentSucceededEvent, self.handle_payment_succeeded)
        self.event_bus.subscribe(PaymentFailedEvent, self.handle_payment_failed)
