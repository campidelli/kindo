import uuid

from sqlmodel import Session, select

from app.modules.trips.models import Trip


class TripRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Trip]:
        return self.session.exec(select(Trip)).all()

    def get_by_id(self, trip_id: uuid.UUID) -> Trip | None:
        return self.session.get(Trip, trip_id)
