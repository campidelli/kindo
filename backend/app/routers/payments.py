import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.schemas import PaymentCreatedResponse, PaymentDetailResponse, PaymentListResponse, PaymentRequest
from app.services.payment_service import PaymentData, PaymentService, TripNotFoundError

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

DbDep = Annotated[Session, Depends(get_session)]


def get_payment_service(db: DbDep) -> PaymentService:
    return PaymentService(db)


PaymentServiceDep = Annotated[PaymentService, Depends(get_payment_service)]


@router.get("", response_model=PaymentListResponse, status_code=status.HTTP_200_OK)
def list_payments(service: PaymentServiceDep):
    """List all payments ordered by most recent first."""
    payments = service.list_payments()
    return PaymentListResponse(
        payments=[
            PaymentDetailResponse(
                id=p.id,
                trip_id=p.trip_id,
                student_name=p.student_name,
                parent_name=p.parent_name,
                card_last_four=p.card_last_four,
                status=p.status.value,
                transaction_id=p.transaction_id,
                error_message=p.error_message,
                created_at=p.created_at,
            )
            for p in payments
        ],
        total=len(payments),
    )


@router.post("", response_model=PaymentCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_payment(body: PaymentRequest, background_tasks: BackgroundTasks, service: PaymentServiceDep):
    data = PaymentData(
        trip_id=body.trip_id,
        student_name=body.student_name,
        parent_name=body.parent_name,
        card_number=body.card_number,
        expiry_date=body.expiry_date,
        cvv=body.cvv,
    )
    try:
        result = service.create_pending_payment(data)
    except TripNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.") from exc

    data.payment_id = result.id
    background_tasks.add_task(service.process_pending_payment, data)

    return PaymentCreatedResponse(
        payment_id=result.id,
        status=result.status.value,
        trip_id=result.trip_id,
        created_at=result.created_at,
    )


@router.get("/{payment_id}", response_model=PaymentDetailResponse, status_code=status.HTTP_200_OK)
def get_payment(payment_id: uuid.UUID, service: PaymentServiceDep):
    payment = service.get_payment_by_id(payment_id)
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found.")

    return PaymentDetailResponse(
        id=payment.id,
        trip_id=payment.trip_id,
        student_name=payment.student_name,
        parent_name=payment.parent_name,
        card_last_four=payment.card_last_four,
        status=payment.status.value,
        transaction_id=payment.transaction_id,
        error_message=payment.error_message,
        created_at=payment.created_at,
    )
