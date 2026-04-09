import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class PaymentStatus(str, enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


class BaseModel(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Trip(BaseModel, table=True):
    __tablename__ = "trips"

    title: str
    description: str
    date: datetime
    location: str
    cost: float
    school_id: str
    activity_id: str

    payments: list["Payment"] = Relationship(back_populates="trip")


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
