import uuid
from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.shared.base import BaseModel

if TYPE_CHECKING:
    from app.modules.bookings.models import Booking


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class Payment(BaseModel, table=True):
    __tablename__ = "payments"

    booking_id: uuid.UUID = Field(foreign_key="bookings.id")
    card_last_four: str
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None

    booking: "Booking" = Relationship()

