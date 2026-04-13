import uuid

from sqlmodel import Session, select

from app.modules.bookings.models import Booking, BookingStatus


class BookingRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[Booking]:
        return self.session.exec(select(Booking)).all()

    def get_by_id(self, booking_id: uuid.UUID) -> Booking | None:
        return self.session.get(Booking, booking_id)

    def create(self, booking: Booking) -> Booking:
        self.session.add(booking)
        self.session.commit()
        self.session.refresh(booking)
        return booking

    def get_by_trip_id(self, trip_id: uuid.UUID) -> list[Booking]:
        return self.session.exec(select(Booking).where(Booking.trip_id == trip_id)).all()

    def cancel(self, booking_id: uuid.UUID) -> Booking | None:
        booking = self.session.get(Booking, booking_id)
        if booking:
            booking.status = BookingStatus.CANCELLED
            self.session.add(booking)
            self.session.commit()
            self.session.refresh(booking)
        return booking

    def update_status(self, booking_id: uuid.UUID, status: BookingStatus) -> Booking | None:
        booking = self.session.get(Booking, booking_id)
        if booking:
            booking.status = status
            self.session.add(booking)
            self.session.commit()
            self.session.refresh(booking)
        return booking
