import uuid

from sqlmodel import Session, select

from app.models import Payment, PaymentStatus


class PaymentRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, payment: Payment) -> Payment:
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment

    def get_by_id(self, payment_id: uuid.UUID) -> Payment | None:
        return self.session.get(Payment, payment_id)

    def list_all(self) -> list[Payment]:
        return list(self.session.exec(select(Payment).order_by(Payment.created_at.desc())).all())

    def update_result(
        self,
        payment_id: uuid.UUID,
        status: PaymentStatus,
        transaction_id: str | None,
        error_message: str | None,
    ) -> Payment | None:
        payment = self.get_by_id(payment_id)
        if payment is None:
            return None

        payment.status = status
        payment.transaction_id = transaction_id
        payment.error_message = error_message
        self.session.add(payment)
        self.session.commit()
        self.session.refresh(payment)
        return payment
