"""Shared test fixtures and helpers."""
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.enums.payment_status import PaymentStatus
from app.models.payment import Payment
from app.models.trip import Trip


def make_trip(**kwargs) -> Trip:
    defaults = dict(
        id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        title="Wellington Zoo Field Trip",
        description="A fun trip",
        date=datetime(2026, 6, 15),
        location="Wellington Zoo",
        cost=35.00,
        school_id="SCH-001",
        activity_id="ACT-ZOO-2026",
    )
    return Trip(**{**defaults, **kwargs})


def make_payment(**kwargs) -> Payment:
    defaults = dict(
        id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        trip_id=uuid.uuid4(),
        student_name="Alice Smith",
        parent_name="Bob Smith",
        card_last_four="1111",
        status=PaymentStatus.PENDING,
        transaction_id=None,
        error_message=None,
    )
    return Payment(**{**defaults, **kwargs})


def mock_session() -> MagicMock:
    return MagicMock()
