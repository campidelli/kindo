import uuid
from enum import Enum
from typing import Optional

from sqlmodel import Field

from app.shared.base import BaseModel


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

