import uuid
from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.shared.base import BaseModel

if TYPE_CHECKING:
    from app.modules.trips.models import Trip


class BookingStatus(str, Enum):
    PENDING_PAYMENT = "PENDING_PAYMENT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class Booking(BaseModel, table=True):
    __tablename__ = "bookings"

    trip_id: uuid.UUID = Field(foreign_key="trip.id")
    status: BookingStatus = Field(default=BookingStatus.PENDING_PAYMENT)
    parent_name: str
    child_name: str
    notes: str = ""

    trip: "Trip" = Relationship(back_populates="bookings")
