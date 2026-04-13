import uuid
from enum import Enum

from sqlmodel import Field

from app.shared.base import BaseModel


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class Booking(BaseModel, table=True):
    __tablename__ = "bookings"

    trip_id: uuid.UUID = Field(foreign_key="trips.id")
    status: BookingStatus = Field(default=BookingStatus.PENDING_PAYMENT)
    parent_name: str
    child_name: str

