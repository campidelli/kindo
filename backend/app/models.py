from datetime import datetime
from typing import Optional

from sqlmodel import Field, Relationship, SQLModel


class Trip(SQLModel, table=True):
    __tablename__ = "trips"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    date: str  # stored as ISO string: YYYY-MM-DD
    location: str
    cost: float
    school_id: str
    activity_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    payments: list["Payment"] = Relationship(back_populates="trip")


class Payment(SQLModel, table=True):
    __tablename__ = "payments"

    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trips.id")
    student_name: str
    parent_name: str
    card_last_four: str
    status: str  # "success" | "failed"
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    trip: Optional["Trip"] = Relationship(back_populates="payments")
