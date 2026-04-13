import uuid

from app.shared.event_bus import Event


class PaymentCreatedEvent(Event):
    """Event published when a payment is created"""

    payment_id: uuid.UUID
    booking_id: uuid.UUID


class PaymentSucceededEvent(Event):
    """Event published when a payment is successfully processed"""

    payment_id: uuid.UUID
    booking_id: uuid.UUID
    transaction_id: str


class PaymentFailedEvent(Event):
    """Event published when a payment fails"""

    payment_id: uuid.UUID
    booking_id: uuid.UUID
    error_message: str
