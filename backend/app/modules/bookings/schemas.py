import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.bookings.models import BookingStatus


class BookingCreateRequest(BaseModel):
    trip_id: uuid.UUID
    parent_name: str = Field(..., min_length=1)
    child_name: str = Field(..., min_length=1)


class BookingResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    status: BookingStatus
    parent_name: str
    child_name: str
    created_at: datetime

    model_config = {"from_attributes": True}
