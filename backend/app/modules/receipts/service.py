import uuid

from app.modules.receipts.repository import ReceiptRepository
from app.modules.receipts.schemas import (
	BookingReceiptResponse,
	ReceiptBooking,
	ReceiptPayment,
	ReceiptTrip,
)


class ReceiptService:
	def __init__(self, repository: ReceiptRepository):
		self.repository = repository

	def get_by_booking_id(self, booking_id: uuid.UUID) -> BookingReceiptResponse | None:
		booking = self.repository.get_booking(booking_id)
		if booking is None:
			return None

		trip = self.repository.get_trip(booking.trip_id)
		payment = self.repository.get_latest_payment_for_booking(booking_id)
		if trip is None or payment is None:
			return None

		return BookingReceiptResponse(
			booking=ReceiptBooking.model_validate(booking),
			trip=ReceiptTrip.model_validate(trip),
			payment=ReceiptPayment.model_validate(payment),
		)
