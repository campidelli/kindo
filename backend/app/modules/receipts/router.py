import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.infrastructure.database import get_session
from app.modules.receipts.repository import ReceiptRepository
from app.modules.receipts.schemas import BookingReceiptResponse
from app.modules.receipts.service import ReceiptService

router = APIRouter(prefix="/api/v1/receipts", tags=["receipts"])

DbDep = Annotated[Session, Depends(get_session)]


def get_receipt_service(db: DbDep) -> ReceiptService:
	return ReceiptService(ReceiptRepository(db))


ReceiptServiceDep = Annotated[ReceiptService, Depends(get_receipt_service)]


@router.get("/bookings/{booking_id}", response_model=BookingReceiptResponse)
def get_booking_receipt(booking_id: uuid.UUID, service: ReceiptServiceDep):
	receipt = service.get_by_booking_id(booking_id)
	if receipt is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Receipt not found for booking.",
		)
	return receipt
