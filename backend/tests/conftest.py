import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.infrastructure.database import get_session
from app.infrastructure.service_factories import (
    build_booking_service_factory,
    build_payment_service_factory,
)
from app.modules.bookings.handlers import BookingEventHandlers
from app.modules.bookings.models import Booking, BookingStatus
from app.modules.bookings.router import router as bookings_router
from app.modules.payments.handlers import PaymentEventHandlers
from app.modules.payments.models import Payment, PaymentStatus
from app.modules.payments.router import router as payments_router
from app.modules.payments.safe_in_memory_card_store import get_card_store
from app.modules.receipts.router import router as receipts_router
from app.modules.trips.models import Trip
from app.modules.trips.router import router as trips_router
from app.shared.event_bus import EventBus, get_event_bus


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


def make_booking(**kwargs) -> Booking:
    defaults = dict(
        id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        trip_id=uuid.uuid4(),
        status=BookingStatus.PENDING_PAYMENT,
        parent_name="Bob Smith",
        child_name="Alice Smith",
    )
    booking = Booking(**{**defaults, **kwargs})
    trip = kwargs.get("trip")
    if trip is not None:
        booking.trip = trip
        booking.trip_id = trip.id
    return booking


def make_payment(**kwargs) -> Payment:
    defaults = dict(
        id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        booking_id=uuid.uuid4(),
        card_last_four="1111",
        status=PaymentStatus.PENDING,
        transaction_id=None,
        error_message=None,
    )
    payment = Payment(**{**defaults, **kwargs})
    booking = kwargs.get("booking")
    if booking is not None:
        payment.booking = booking
        payment.booking_id = booking.id
    return payment


@pytest.fixture
def session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as test_session:
        yield test_session


@pytest.fixture
def event_bus() -> EventBus:
    bus = EventBus()
    yield bus
    bus.reset()


@pytest.fixture
def card_store():
    store = get_card_store()
    store.reset()
    yield store
    store.reset()


@pytest.fixture
def client(session: Session, event_bus: EventBus, card_store) -> TestClient:
    def override_get_session():
        yield session

    def override_get_event_bus() -> EventBus:
        return event_bus

    @contextmanager
    def test_session_scope():
        yield session

    event_bus.reset()
    booking_service_factory = build_booking_service_factory(test_session_scope, event_bus)
    payment_service_factory = build_payment_service_factory(test_session_scope, event_bus, card_store)
    BookingEventHandlers(booking_service_factory, event_bus).register_handlers()
    PaymentEventHandlers(payment_service_factory, event_bus).register_handlers()

    app = FastAPI(title="Test App", version="1.0.0")
    app.include_router(trips_router)
    app.include_router(bookings_router)
    app.include_router(payments_router)
    app.include_router(receipts_router)
    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_event_bus] = override_get_event_bus

    with TestClient(app) as test_client:
        yield test_client
