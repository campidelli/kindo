import uuid
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.models.base import BaseModel
from app.enums.payment_status import PaymentStatus

if TYPE_CHECKING:
    from app.models.trip import Trip


class Payment(BaseModel, table=True):
    __tablename__ = "payments"

    trip_id: uuid.UUID = Field(foreign_key="trips.id")
    student_name: str
    parent_name: str
    card_last_four: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None

    trip: Optional["Trip"] = Relationship(back_populates="payments")
