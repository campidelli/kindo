import uuid
from datetime import datetime

from pydantic import BaseModel

from app.modules.bookings.models import BookingStatus
from app.modules.payments.models import PaymentStatus


class ReceiptTrip(BaseModel):
	id: uuid.UUID
	title: str
	description: str
	date: datetime
	location: str
	cost: float
	school_id: str
	activity_id: str


class ReceiptBooking(BaseModel):
	id: uuid.UUID
	trip_id: uuid.UUID
	status: BookingStatus
	parent_name: str
	child_name: str
	created_at: datetime


class ReceiptPayment(BaseModel):
	id: uuid.UUID
	booking_id: uuid.UUID
	card_last_four: str
	status: PaymentStatus
	transaction_id: str | None
	error_message: str | None
	created_at: datetime


class BookingReceiptResponse(BaseModel):
	booking: ReceiptBooking
	trip: ReceiptTrip
	payment: ReceiptPayment
