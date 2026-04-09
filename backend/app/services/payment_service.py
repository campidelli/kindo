import asyncio

from legacy_payment import LegacyPaymentProcessor, PaymentResponse

_processor = LegacyPaymentProcessor()


async def charge(
    student_name: str,
    parent_name: str,
    amount: float,
    card_number: str,
    expiry_date: str,
    cvv: str,
    school_id: str,
    activity_id: str,
) -> PaymentResponse:
    """Call the blocking legacy processor on a thread-pool thread."""
    payment_data = {
        "student_name": student_name,
        "parent_name": parent_name,
        "amount": amount,
        "card_number": card_number.replace(" ", ""),
        "expiry_date": expiry_date,
        "cvv": cvv,
        "school_id": school_id,
        "activity_id": activity_id,
    }
    return await asyncio.to_thread(_processor.process_payment, payment_data)
