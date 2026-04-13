import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Relationship

from app.shared.base import BaseModel

if TYPE_CHECKING:
    from app.modules.bookings.models import Booking
    from app.modules.payments.models import Payment


class Trip(BaseModel, table=True):
    __tablename__ = "trips"

    title: str
    description: str
    date: datetime
    location: str
    cost: float
    school_id: str
    activity_id: str

    bookings: list["Booking"] = Relationship(back_populates="trip")
    payments: list["Payment"] = Relationship(back_populates="trip")
