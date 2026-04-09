import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.enums.payment_status import PaymentStatus
from app.integrations.legacy_payment_processor import PaymentResponse
from app.services.payment_service import (
    PaymentData,
    PaymentNotFoundError,
    PaymentService,
    TripNotFoundError,
)
from tests.conftest import make_payment, make_trip


def make_service(trip_repo: MagicMock, payment_repo: MagicMock) -> PaymentService:
    service = PaymentService.__new__(PaymentService)
    service.trip_repository = trip_repo
    service.payment_repository = payment_repo
    return service


def payment_data(**kwargs) -> PaymentData:
    defaults = dict(
        trip_id=uuid.uuid4(),
        student_name="Alice Smith",
        parent_name="Bob Smith",
        card_number="4111 1111 1111 1111",
        expiry_date="12/30",
        cvv="123",
    )
    return PaymentData(**{**defaults, **kwargs})


# ---------------------------------------------------------------------------
# create_pending_payment
# ---------------------------------------------------------------------------

class TestCreatePendingPayment:
    def test_creates_payment_with_pending_status(self):
        trip = make_trip()
        payment = make_payment(trip_id=trip.id, status=PaymentStatus.PENDING)

        trip_repo = MagicMock()
        trip_repo.get_by_id.return_value = trip
        payment_repo = MagicMock()
        payment_repo.create.return_value = payment

        result = make_service(trip_repo, payment_repo).create_pending_payment(payment_data(trip_id=trip.id))

        assert result.status == PaymentStatus.PENDING
        assert result.trip_id == trip.id
        payment_repo.create.assert_called_once()

    def test_extracts_last_four_from_card_number(self):
        trip = make_trip()

        trip_repo = MagicMock()
        trip_repo.get_by_id.return_value = trip
        payment_repo = MagicMock()
        payment_repo.create.return_value = make_payment(trip_id=trip.id, card_last_four="1111")

        make_service(trip_repo, payment_repo).create_pending_payment(
            payment_data(trip_id=trip.id, card_number="4111 1111 1111 1111")
        )

        created: object = payment_repo.create.call_args[0][0]
        assert created.card_last_four == "1111"

    def test_raises_when_trip_not_found(self):
        trip_repo = MagicMock()
        trip_repo.get_by_id.return_value = None
        payment_repo = MagicMock()

        with pytest.raises(TripNotFoundError):
            make_service(trip_repo, payment_repo).create_pending_payment(payment_data())

        payment_repo.create.assert_not_called()


# ---------------------------------------------------------------------------
# get_payment_by_id
# ---------------------------------------------------------------------------

class TestGetPaymentById:
    def test_returns_payment_when_found(self):
        payment = make_payment()
        trip_repo = MagicMock()
        payment_repo = MagicMock()
        payment_repo.get_by_id.return_value = payment

        result = make_service(trip_repo, payment_repo).get_payment_by_id(payment.id)

        assert result == payment

    def test_returns_none_when_not_found(self):
        trip_repo = MagicMock()
        payment_repo = MagicMock()
        payment_repo.get_by_id.return_value = None

        result = make_service(trip_repo, payment_repo).get_payment_by_id(uuid.uuid4())

        assert result is None


# ---------------------------------------------------------------------------
# process_pending_payment
# ---------------------------------------------------------------------------

class TestProcessPendingPayment:
    @pytest.fixture
    def trip(self):
        return make_trip()

    @pytest.fixture
    def pending_payment(self, trip):
        return make_payment(trip_id=trip.id, status=PaymentStatus.PENDING)

    def _make_repos(self, trip, pending_payment, updated_payment):
        trip_repo = MagicMock()
        trip_repo.get_by_id.return_value = trip

        payment_repo = MagicMock()
        payment_repo.get_by_id.return_value = pending_payment
        payment_repo.update_result.return_value = updated_payment
        return trip_repo, payment_repo

    async def test_updates_payment_to_success(self, trip, pending_payment):
        success_payment = make_payment(
            id=pending_payment.id,
            trip_id=trip.id,
            status=PaymentStatus.SUCCESS,
            transaction_id="TXN-123",
        )
        trip_repo, payment_repo = self._make_repos(trip, pending_payment, success_payment)
        data = payment_data(trip_id=trip.id, payment_id=pending_payment.id)

        processor_response = PaymentResponse(success=True, transaction_id="TXN-123")
        with patch("app.services.payment_service.asyncio.to_thread", new=AsyncMock(return_value=processor_response)), \
             patch("app.services.payment_service.Session") as mock_session_cls:
            mock_session_cls.return_value.__enter__.return_value.exec = MagicMock()
            mock_session = MagicMock()
            mock_session.__enter__ = MagicMock(return_value=mock_session)
            mock_session.__exit__ = MagicMock(return_value=False)
            mock_payment_repo = MagicMock()
            mock_payment_repo.update_result.return_value = success_payment
            mock_session_cls.return_value.__enter__.return_value = mock_session

            service = make_service(trip_repo, payment_repo)

            with patch("app.services.payment_service.PaymentRepository", return_value=mock_payment_repo):
                result = await service.process_pending_payment(data)

        mock_payment_repo.update_result.assert_called_once_with(
            payment_id=pending_payment.id,
            status=PaymentStatus.SUCCESS,
            transaction_id="TXN-123",
            error_message=None,
        )
        assert result == success_payment

    async def test_updates_payment_to_failed_on_processor_error(self, trip, pending_payment):
        failed_payment = make_payment(
            id=pending_payment.id,
            trip_id=trip.id,
            status=PaymentStatus.FAILED,
            error_message="Insufficient funds",
        )
        trip_repo, payment_repo = self._make_repos(trip, pending_payment, failed_payment)
        data = payment_data(trip_id=trip.id, payment_id=pending_payment.id)

        processor_response = PaymentResponse(success=False, error_message="Insufficient funds")
        with patch("app.services.payment_service.asyncio.to_thread", new=AsyncMock(return_value=processor_response)), \
             patch("app.services.payment_service.PaymentRepository") as mock_repo_cls:
            mock_payment_repo = MagicMock()
            mock_payment_repo.update_result.return_value = failed_payment
            mock_repo_cls.return_value = mock_payment_repo

            with patch("app.services.payment_service.Session"):
                result = await make_service(trip_repo, payment_repo).process_pending_payment(data)

        mock_payment_repo.update_result.assert_called_once_with(
            payment_id=pending_payment.id,
            status=PaymentStatus.FAILED,
            transaction_id=None,
            error_message="Insufficient funds",
        )
        assert result == failed_payment

    async def test_raises_when_payment_not_found(self, trip):
        trip_repo = MagicMock()
        payment_repo = MagicMock()
        payment_repo.get_by_id.return_value = None
        data = payment_data(trip_id=trip.id, payment_id=uuid.uuid4())

        with pytest.raises(PaymentNotFoundError):
            await make_service(trip_repo, payment_repo).process_pending_payment(data)

    async def test_raises_when_trip_not_found_during_processing(self, pending_payment):
        trip_repo = MagicMock()
        trip_repo.get_by_id.return_value = None
        payment_repo = MagicMock()
        payment_repo.get_by_id.return_value = pending_payment
        data = payment_data(trip_id=pending_payment.trip_id, payment_id=pending_payment.id)

        with pytest.raises(TripNotFoundError):
            await make_service(trip_repo, payment_repo).process_pending_payment(data)
