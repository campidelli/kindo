from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_db
from app.models import Payment, Trip
from app.schemas import PaymentRequest, PaymentResponse
from app.services import payment_service

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])

DbDep = Annotated[Session, Depends(get_db)]


@router.post("", response_model=PaymentResponse, status_code=200)
async def create_payment(body: PaymentRequest, db: DbDep):
    trip = db.get(Trip, body.trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")

    result = await payment_service.charge(
        student_name=body.student_name,
        parent_name=body.parent_name,
        amount=trip.cost,
        card_number=body.card_number,
        expiry_date=body.expiry_date,
        cvv=body.cvv,
        school_id=trip.school_id,
        activity_id=trip.activity_id,
    )

    card_last_four = body.card_number.replace(" ", "")[-4:]

    payment = Payment(
        trip_id=body.trip_id,
        student_name=body.student_name,
        parent_name=body.parent_name,
        card_last_four=card_last_four,
        status="success" if result.success else "failed",
        transaction_id=result.transaction_id,
        error_message=result.error_message,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    return PaymentResponse(
        success=result.success,
        payment_id=payment.id,
        transaction_id=result.transaction_id,
        error_message=result.error_message,
    )
