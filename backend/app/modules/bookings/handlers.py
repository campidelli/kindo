import logging

from app.modules.bookings.events import BookingCreatedEvent
from app.shared.event_bus import event_bus

logger = logging.getLogger(__name__)


def handle_booking_created(event: BookingCreatedEvent) -> None:
    """Handler for BookingCreatedEvent"""
    logger.info(
        f"Booking created: booking_id={event.booking_id}, trip_id={event.trip_id}, parent_name={event.parent_name}, child_name={event.child_name}"
    )
    # Add additional logic here (e.g., send notifications, update analytics, etc.)


def register_handlers() -> None:
    """Register all event handlers"""
    event_bus.subscribe(BookingCreatedEvent, handle_booking_created)
