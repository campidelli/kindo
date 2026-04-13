import re
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.modules.payments.models import PaymentStatus


class PaymentCreateRequest(BaseModel):
    booking_id: uuid.UUID
    card_number: str = Field(..., description="16-digit card number")
    cvv: str = Field(..., description="3-digit CVV")
    expiry_month: int = Field(..., ge=1, le=12, description="Expiry month in MM format")
    expiry_year: int = Field(..., ge=0, le=9999, description="Expiry year in YY or YYYY format")

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, value: str) -> str:
        digits = value.replace(" ", "")
        if not digits.isdigit() or len(digits) != 16:
            raise ValueError("Card number must be 16 digits.")
        return value

    @field_validator("cvv")
    @classmethod
    def validate_cvv(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 3:
            raise ValueError("CVV must be 3 digits.")
        return value

    @field_validator("expiry_year")
    @classmethod
    def validate_expiry_year(cls, value: int) -> int:
        if not re.fullmatch(r"\d{2}|\d{4}", str(value)):
            raise ValueError("Expiry year must be 2 or 4 digits.")
        return value


class PaymentResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    card_last_four: str
    status: PaymentStatus
    transaction_id: str | None
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
