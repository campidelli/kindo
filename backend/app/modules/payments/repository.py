import uuid

from sqlmodel import Session, select

from app.modules.payments.models import Payment


class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Payment]:
        return self.session.exec(select(Payment)).all()

    def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        return self.session.get(Payment, payment_id)

    def create(self, payment: Payment) -> Payment:
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def get_by_booking_id(self, booking_id: uuid.UUID) -> list[Payment]:
        return self.session.exec(select(Payment).where(Payment.booking_id == booking_id)).all()

    def update(self, payment: Payment) -> Payment:
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment
