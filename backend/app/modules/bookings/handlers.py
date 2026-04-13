import logging

from app.modules.bookings.events import BookingCancelledEvent, BookingCreatedEvent
from app.shared.event_bus import event_bus

logger = logging.getLogger(__name__)


def handle_booking_created(event: BookingCreatedEvent) -> None:
    """Handler for BookingCreatedEvent"""
    logger.info(
        f"Booking created: booking_id={event.booking_id}, trip_id={event.trip_id}, parent_name={event.parent_name}, child_name={event.child_name}"
    )
    # Add additional logic here (e.g., send notifications, update analytics, etc.)


def handle_booking_cancelled(event: BookingCancelledEvent) -> None:
    """Handler for BookingCancelledEvent"""
    logger.info(
        f"Booking cancelled: booking_id={event.booking_id}, trip_id={event.trip_id}, parent_name={event.parent_name}, child_name={event.child_name}"
    )
    # Add additional logic here (e.g., send notifications, refund processing, etc.)


def register_handlers() -> None:
    """Register all event handlers"""
    event_bus.subscribe(BookingCreatedEvent, handle_booking_created)
    event_bus.subscribe(BookingCancelledEvent, handle_booking_cancelled)
