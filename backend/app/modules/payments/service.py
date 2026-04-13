import logging
import uuid

from app.modules.payments.events import PaymentSucceededEvent, PaymentCreatedEvent, PaymentFailedEvent
from app.modules.payments.legacy_payment_processor import LegacyPaymentProcessor
from app.modules.payments.models import Payment, PaymentStatus
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.safe_in_memory_card_store import CardData, get_card_store
from app.modules.bookings.repository import BookingRepository
from app.shared.event_bus import EventBus

logger = logging.getLogger(__name__)
payment_processor = LegacyPaymentProcessor()


class PaymentService:
    def __init__(
        self,
        card_store: get_card_store,
        repository: PaymentRepository,
        booking_repository: BookingRepository,
        event_bus: EventBus,
    ):
        self.repository = repository
        self.booking_repository = booking_repository
        self.card_store = card_store
        self.event_bus = event_bus

    def get_all(self) -> list[Payment]:
        return self.repository.get_all()

    def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        return self.repository.get_by_id(payment_id)

    def get_by_booking_id(self, booking_id: uuid.UUID) -> list[Payment]:
        return self.repository.get_by_booking_id(booking_id)

    def create(
        self,
        booking_id: uuid.UUID,
        card_last_four: str,
        card_number: str,
        cvv: str,
        expiry_date: str,
    ) -> Payment:
        logger.info(f"Creating payment for booking_id={booking_id}, card_last_four={card_last_four}")
        payment = Payment(
            booking_id=booking_id,
            card_last_four=card_last_four,
            status=PaymentStatus.PENDING,
        )
        created_payment = self.repository.create(payment)
        logger.info(f"Payment created: payment_id={created_payment.id}, booking_id={booking_id}")

        # NOTE: In a real application, the payment provider is called by the frontend and a token is sent to the backend,
        # so we don't handle raw card data in the backend at all.
        logger.debug(f"Storing card data in memory for payment_id={created_payment.id}")
        card_store = get_card_store()
        card_data = CardData(
            card_number=card_number,
            cvv=cvv,
            expiry_date=expiry_date,
        )
        card_store.store(created_payment.id, card_data)

        self.event_bus.publish(PaymentCreatedEvent(payment_id=created_payment.id, booking_id=created_payment.booking_id))

        return created_payment

    def process(self, payment_id: uuid.UUID) -> Payment | None:
        """Process a payment - retrieve card data and initiate payment processing"""
        logger.info(f"Starting payment processing for payment_id={payment_id}")

        payment = self.repository.get_by_id(payment_id)
        if payment is None:
            logger.warning(f"Payment not found: payment_id={payment_id}")
            return None

        if payment.status == PaymentStatus.SUCCESS:
            logger.info(f"Payment already successful: payment_id={payment_id}")
            return payment

        if payment.status != PaymentStatus.PENDING:
            logger.info(f"Payment cannot be processed: payment_id={payment_id}, status={payment.status}")
            return payment

        logger.info(f"Retrieving card data for payment_id={payment_id}")
        card_data = self.card_store.get(payment_id)
        if card_data is None:
            logger.error(f"Card data not found for payment_id={payment_id}, failing payment")
            return self._fail_payment(payment, "Card data not found")

        logger.info(f"Processing payment with payment provider for payment_id={payment_id}")
        booking = self.booking_repository.get_by_id(payment.booking_id)
        if booking is None:
            logger.error(f"Booking not found for payment_id={payment_id}")
            return self._fail_payment(payment, "Booking not found")

        payment_data = {
            "student_name": booking.child_name,
            "parent_name": booking.parent_name,
            "amount": booking.trip.cost,
            "card_number": card_data.card_number,
            "expiry_date": card_data.expiry_date,
            "cvv": card_data.cvv,
            "school_id": booking.trip.school_id,
            "activity_id": booking.trip.activity_id,
        }
        logger.debug(f"Calling legacy payment processor with payment_data for payment_id={payment_id}")
        response = payment_processor.process_payment(payment_data)

        logger.debug(f"Removing card data from store for payment_id={payment_id}")
        self.card_store.remove(payment_id)

        if not response.success:
            logger.error(f"Payment processing failed for payment_id={payment_id}: {response.error_message}")
            return self._fail_payment(payment, response.error_message)

        logger.info(f"Payment processed successfully for payment_id={payment_id}")
        payment.status = PaymentStatus.SUCCESS
        payment.transaction_id = response.transaction_id
        updated_payment = self.repository.update(payment)

        logger.info(f"Payment succeeded: payment_id={payment_id}, transaction_id={payment.transaction_id}")
        self.event_bus.publish(PaymentSucceededEvent(payment_id=payment.id, booking_id=payment.booking_id, transaction_id=payment.transaction_id))

        return updated_payment

    def _fail_payment(self, payment: Payment, error_message: str) -> Payment:
        payment.status = PaymentStatus.FAILED
        payment.error_message = error_message
        self.repository.update(payment)
        self.event_bus.publish(PaymentFailedEvent(payment_id=payment.id, booking_id=payment.booking_id, error_message=error_message))
        return payment
