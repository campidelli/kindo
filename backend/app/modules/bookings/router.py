import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.infrastructure.database import get_session
from app.modules.bookings.models import Booking
from app.modules.bookings.repository import BookingRepository
from app.modules.bookings.schemas import BookingCreateRequest, BookingResponse
from app.modules.bookings.service import BookingService

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])

DbDep = Annotated[Session, Depends(get_session)]


def get_booking_service(db: DbDep) -> BookingService:
    return BookingService(BookingRepository(db))


BookingServiceDep = Annotated[BookingService, Depends(get_booking_service)]


@router.get("", response_model=list[BookingResponse])
def list_bookings(service: BookingServiceDep):
    return service.get_all()


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: uuid.UUID, service: BookingServiceDep):
    booking = service.get_by_id(booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return booking


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(request: BookingCreateRequest, service: BookingServiceDep):
    booking = Booking(**request.model_dump())
    return service.create(booking)


@router.delete("/{booking_id}", response_model=BookingResponse) 
def cancel_booking(booking_id: uuid.UUID, service: BookingServiceDep):
    booking = service.cancel(booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")
    return booking
