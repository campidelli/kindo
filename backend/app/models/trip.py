import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.payment import Payment


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
