import uuid
from unittest.mock import MagicMock, patch

from app.modules.payments.events import PaymentCreatedEvent, PaymentFailedEvent, PaymentSucceededEvent
from app.modules.payments.legacy_payment_processor import PaymentResponse
from app.modules.payments.models import PaymentStatus
from app.modules.payments.safe_in_memory_card_store import CardData, SafeInMemoryCardStore
from app.modules.payments.service import PaymentService
from tests.conftest import make_booking, make_payment, make_trip


def make_service(
    card_store: SafeInMemoryCardStore,
    payment_repository: MagicMock,
    booking_repository: MagicMock,
    event_bus: MagicMock,
) -> PaymentService:
    return PaymentService(card_store, payment_repository, booking_repository, event_bus)


class TestPaymentService:
    def test_create_persists_pending_payment_stores_card_data_and_publishes_event(self):
        created_payment = make_payment()
        card_store = SafeInMemoryCardStore()
        payment_repository = MagicMock()
        payment_repository.create.return_value = created_payment
        booking_repository = MagicMock()
        event_bus = MagicMock()

        result = make_service(card_store, payment_repository, booking_repository, event_bus).create(
            booking_id=created_payment.booking_id,
            card_last_four="1111",
            card_number="4111111111111111",
            cvv="123",
            expiry_date="12/30",
        )

        assert result == created_payment
        assert card_store.exists(created_payment.id)
        published_event = event_bus.publish.call_args.args[0]
        assert isinstance(published_event, PaymentCreatedEvent)
        assert published_event.payment_id == created_payment.id
        assert published_event.booking_id == created_payment.booking_id

    def test_get_by_id_returns_none_when_payment_missing(self):
        card_store = SafeInMemoryCardStore()
        payment_repository = MagicMock()
        payment_repository.get_by_id.return_value = None
        booking_repository = MagicMock()
        event_bus = MagicMock()

        result = make_service(card_store, payment_repository, booking_repository, event_bus).get_by_id(uuid.uuid4())

        assert result is None

    def test_process_returns_none_when_payment_does_not_exist(self):
        card_store = SafeInMemoryCardStore()
        payment_repository = MagicMock()
        payment_repository.get_by_id.return_value = None
        booking_repository = MagicMock()
        event_bus = MagicMock()

        result = make_service(card_store, payment_repository, booking_repository, event_bus).process(uuid.uuid4())

        assert result is None

    def test_process_fails_when_card_data_is_missing(self):
        payment = make_payment(status=PaymentStatus.PENDING)
        card_store = SafeInMemoryCardStore()
        payment_repository = MagicMock()
        payment_repository.get_by_id.return_value = payment
        payment_repository.update.side_effect = lambda updated_payment: updated_payment
        booking_repository = MagicMock()
        event_bus = MagicMock()

        result = make_service(card_store, payment_repository, booking_repository, event_bus).process(payment.id)

        assert result.status == PaymentStatus.FAILED
        assert result.error_message == "Card data not found"
        published_event = event_bus.publish.call_args.args[0]
        assert isinstance(published_event, PaymentFailedEvent)
        assert published_event.booking_id == payment.booking_id

    def test_process_fails_when_booking_is_missing(self):
        payment = make_payment(status=PaymentStatus.PENDING)
        card_store = SafeInMemoryCardStore()
        card_store.store(payment.id, CardData(card_number="4111111111111111", cvv="123", expiry_date="12/30"))
        payment_repository = MagicMock()
        payment_repository.get_by_id.return_value = payment
        payment_repository.update.side_effect = lambda updated_payment: updated_payment
        booking_repository = MagicMock()
        booking_repository.get_by_id.return_value = None
        event_bus = MagicMock()

        result = make_service(card_store, payment_repository, booking_repository, event_bus).process(payment.id)

        assert result.status == PaymentStatus.FAILED
        assert result.error_message == "Booking not found"
        published_event = event_bus.publish.call_args.args[0]
        assert isinstance(published_event, PaymentFailedEvent)

    def test_process_marks_payment_success_and_publishes_event(self):
        trip = make_trip(cost=42.0, school_id="SCH-TEST", activity_id="ACT-TEST")
        booking = make_booking(trip=trip)
        payment = make_payment(booking=booking, status=PaymentStatus.PENDING)
        updated_payment = make_payment(
            id=payment.id,
            booking=booking,
            status=PaymentStatus.SUCCESS,
            transaction_id="TXN-123",
        )
        card_store = SafeInMemoryCardStore()
        card_store.store(payment.id, CardData(card_number="4111111111111111", cvv="123", expiry_date="12/30"))
        payment_repository = MagicMock()
        payment_repository.get_by_id.return_value = payment
        payment_repository.update.return_value = updated_payment
        booking_repository = MagicMock()
        booking_repository.get_by_id.return_value = booking
        event_bus = MagicMock()

        with patch(
            "app.modules.payments.service.payment_processor.process_payment",
            return_value=PaymentResponse(success=True, transaction_id="TXN-123"),
        ) as processor:
            result = make_service(card_store, payment_repository, booking_repository, event_bus).process(payment.id)

        assert result == updated_payment
        assert not card_store.exists(payment.id)
        processor.assert_called_once_with(
            {
                "student_name": booking.child_name,
                "parent_name": booking.parent_name,
                "amount": booking.trip.cost,
                "card_number": "4111111111111111",
                "expiry_date": "12/30",
                "cvv": "123",
                "school_id": booking.trip.school_id,
                "activity_id": booking.trip.activity_id,
            }
        )
        published_event = event_bus.publish.call_args.args[0]
        assert isinstance(published_event, PaymentSucceededEvent)
        assert published_event.transaction_id == "TXN-123"

    def test_process_marks_payment_failed_when_processor_rejects_it(self):
        trip = make_trip()
        booking = make_booking(trip=trip)
        payment = make_payment(booking=booking, status=PaymentStatus.PENDING)
        card_store = SafeInMemoryCardStore()
        card_store.store(payment.id, CardData(card_number="4111111111111111", cvv="123", expiry_date="12/30"))
        payment_repository = MagicMock()
        payment_repository.get_by_id.return_value = payment
        payment_repository.update.side_effect = lambda updated_payment: updated_payment
        booking_repository = MagicMock()
        booking_repository.get_by_id.return_value = booking
        event_bus = MagicMock()

        with patch(
            "app.modules.payments.service.payment_processor.process_payment",
            return_value=PaymentResponse(success=False, error_message="Declined"),
        ):
            result = make_service(card_store, payment_repository, booking_repository, event_bus).process(payment.id)

        assert result.status == PaymentStatus.FAILED
        assert result.error_message == "Declined"
        assert not card_store.exists(payment.id)
        published_event = event_bus.publish.call_args.args[0]
        assert isinstance(published_event, PaymentFailedEvent)
