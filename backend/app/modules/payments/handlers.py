import logging

from app.modules.payments.events import PaymentCreatedEvent
from app.modules.payments.service import PaymentService
from app.shared.event_bus import event_bus

logger = logging.getLogger(__name__)


class PaymentEventHandlers:
    def __init__(self, payment_service: PaymentService):
        self.payment_service = payment_service

    def handle_payment_created(self, event: PaymentCreatedEvent) -> None:
        """Handler for PaymentCreatedEvent"""
        logger.info(
          "PaymentCreatedEvent received",
          extra={"payment_id": event.payment_id, "booking_id": event.booking_id}
        )
        self.payment_service.process(event.payment_id)

    def register_handlers(self) -> None:
        """Register all event handlers"""
        event_bus.subscribe(PaymentCreatedEvent, self.handle_payment_created)
