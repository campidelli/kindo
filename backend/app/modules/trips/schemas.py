import uuid
from datetime import datetime

from pydantic import BaseModel


class TripResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    date: datetime
    location: str
    cost: float
    school_id: str
    activity_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
