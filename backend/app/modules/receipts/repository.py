import uuid

from sqlmodel import Session, select

from app.modules.bookings.models import Booking
from app.modules.payments.models import Payment
from app.modules.trips.models import Trip


class ReceiptRepository:
	def __init__(self, session: Session):
		self.session = session

	def get_booking(self, booking_id: uuid.UUID) -> Booking | None:
		return self.session.get(Booking, booking_id)

	def get_trip(self, trip_id: uuid.UUID) -> Trip | None:
		return self.session.get(Trip, trip_id)

	def get_latest_payment_for_booking(self, booking_id: uuid.UUID) -> Payment | None:
		statement = (
			select(Payment)
			.where(Payment.booking_id == booking_id)
			.order_by(Payment.created_at.desc())
		)
		return self.session.exec(statement).first()
