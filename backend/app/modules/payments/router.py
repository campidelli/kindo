import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.infrastructure.database import get_session
from app.modules.bookings.repository import BookingRepository
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.schemas import PaymentCreateRequest, PaymentResponse
from app.modules.payments.service import PaymentService
from app.modules.payments.safe_in_memory_card_store import get_card_store
from app.shared.event_bus import EventBus, get_event_bus

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

DbDep = Annotated[Session, Depends(get_session)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]


def get_payment_service(db: DbDep, event_bus: EventBusDep) -> PaymentService:
    return PaymentService(get_card_store(), PaymentRepository(db), BookingRepository(db), event_bus)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


@router.get("", response_model=list[PaymentResponse])
def list_payments(service: PaymentServiceDep):
    return service.get_all()


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: uuid.UUID, service: PaymentServiceDep):
    payment = service.get_by_id(payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")
    return payment


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def create_payment(request: PaymentCreateRequest, service: PaymentServiceDep):
    # Extract last 4 digits from card
    card_last_four = request.card_number[-4:]

    # Get booking to fetch parent and child names
    booking = service.booking_repository.get_by_id(request.booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found.")

    # Format expiry date as MM/YY
    expiry_date = f"{request.expiry_month:02d}/{str(request.expiry_year)[-2:]}"

    return service.create(
        booking_id=request.booking_id,
        card_last_four=card_last_four,
        card_number=request.card_number,
        cvv=request.cvv,
        expiry_date=expiry_date,
    )
