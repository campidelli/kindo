import uuid
from datetime import datetime

from pydantic import BaseModel

from app.modules.bookings.models import BookingStatus


class BookingCreate(BaseModel):
    trip_id: uuid.UUID
    parent_name: str
    child_name: str
    notes: str = ""


class BookingResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    status: BookingStatus
    parent_name: str
    child_name: str
    notes: str
    created_at: datetime

    model_config = {"from_attributes": True}
