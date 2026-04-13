from datetime import datetime

from app.shared.base import BaseModel


class Trip(BaseModel, table=True):
    __tablename__ = "trips"

    title: str
    description: str
    date: datetime
    location: str
    cost: float
    school_id: str
    activity_id: str

