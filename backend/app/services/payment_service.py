import asyncio
import uuid
from dataclasses import dataclass

from sqlmodel import Session

from app.integrations.legacy_payment_processor import LegacyPaymentProcessor
from app.core.database import engine
from app.models import Payment, PaymentStatus
from app.repositories.payment_repository import PaymentRepository
from app.repositories.trip_repository import TripRepository

_processor = LegacyPaymentProcessor()

class TripNotFoundError(Exception):
    pass

class PaymentNotFoundError(Exception):
    pass

@dataclass
class PaymentData:
    trip_id: uuid.UUID
    student_name: str
    parent_name: str
    card_number: str
    expiry_date: str
    cvv: str
    payment_id: uuid.UUID | None = None

class PaymentService:
    def __init__(self, session: Session):
        self.trip_repository = TripRepository(session)
        self.payment_repository = PaymentRepository(session)

    def create_pending_payment(self, data: PaymentData) -> Payment:
        trip = self.trip_repository.get_by_id(data.trip_id)
        if trip is None:
            raise TripNotFoundError()

        return self.payment_repository.create(
            Payment(
                id=uuid.uuid4(),
                trip_id=trip.id,
                student_name=data.student_name,
                parent_name=data.parent_name,
                card_last_four=data.card_number.replace(" ", "")[-4:],
                status=PaymentStatus.PENDING,
            )
        )

    def get_payment_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        return self.payment_repository.get_by_id(payment_id)

    async def process_pending_payment(self, data: PaymentData) -> Payment:
        payment = self.payment_repository.get_by_id(data.payment_id)
        if payment is None:
            raise PaymentNotFoundError()
        trip = self.trip_repository.get_by_id(payment.trip_id)
        if trip is None:
            raise TripNotFoundError()

        payment_data = {
            "student_name": payment.student_name,
            "parent_name": payment.parent_name,
            "amount": trip.cost,
            "card_number": data.card_number,
            "expiry_date": data.expiry_date,
            "cvv": data.cvv,
            "school_id": trip.school_id,
            "activity_id": trip.activity_id,
        }
        result = await asyncio.to_thread(_processor.process_payment, payment_data)

        with Session(engine) as session:
            repository = PaymentRepository(session)
            payment = repository.update_result(
                payment_id=payment.id,
                status=PaymentStatus.SUCCESS if result.success else PaymentStatus.FAILED,
                transaction_id=result.transaction_id,
                error_message=result.error_message,
            )
        return payment
