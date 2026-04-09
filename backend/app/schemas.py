import re
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Trip schemas
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Payment schemas
# ---------------------------------------------------------------------------

class PaymentRequest(BaseModel):
    trip_id: uuid.UUID
    student_name: str = Field(..., min_length=1)
    parent_name: str = Field(..., min_length=1)
    card_number: str = Field(..., description="16-digit card number")
    expiry_date: str = Field(..., description="Expiry date in MM/YY format")
    cvv: str = Field(..., description="3-digit CVV")

    @field_validator("card_number")
    @classmethod
    def validate_card_number(cls, v: str) -> str:
        digits = v.replace(" ", "")
        if not digits.isdigit() or len(digits) != 16:
            raise ValueError("Card number must be 16 digits.")
        return v

    @field_validator("expiry_date")
    @classmethod
    def validate_expiry_date(cls, v: str) -> str:
        if not re.fullmatch(r"(0[1-9]|1[0-2])/\d{2}", v):
            raise ValueError("Expiry date must be in MM/YY format.")
        return v

    @field_validator("cvv")
    @classmethod
    def validate_cvv(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 3:
            raise ValueError("CVV must be 3 digits.")
        return v


class PaymentResponse(BaseModel):
    success: bool
    payment_id: uuid.UUID
    transaction_id: str | None = None
    error_message: str | None = None

    model_config = {"from_attributes": True}
