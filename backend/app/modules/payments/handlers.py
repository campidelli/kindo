import logging

from app.modules.payments.events import PaymentCreatedEvent
from app.modules.payments.service import PaymentService
from app.shared.event_bus import EventBus

logger = logging.getLogger(__name__)


class PaymentEventHandlers:
    def __init__(self, payment_service: PaymentService, event_bus: EventBus):
        self.payment_service = payment_service
        self.event_bus = event_bus

    def handle_payment_created(self, event: PaymentCreatedEvent) -> None:
        """Handler for PaymentCreatedEvent"""
        logger.info(
          "PaymentCreatedEvent received",
          extra={"payment_id": event.payment_id, "booking_id": event.booking_id}
        )
        self.payment_service.process(event.payment_id)

    def register_handlers(self) -> None:
        """Register all event handlers"""
        self.event_bus.subscribe(PaymentCreatedEvent, self.handle_payment_created)
