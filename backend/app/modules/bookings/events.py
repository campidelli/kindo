import uuid

from app.shared.event_bus import Event


class BookingCreatedEvent(Event):
    """Event published when a booking is created"""

    booking_id: uuid.UUID
    trip_id: uuid.UUID
    parent_name: str
    child_name: str


class BookingCancelledEvent(Event):
    """Event published when a booking is cancelled"""

    booking_id: uuid.UUID
    trip_id: uuid.UUID
    parent_name: str
    child_name: str
