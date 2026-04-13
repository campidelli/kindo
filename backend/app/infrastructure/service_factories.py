from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager

from sqlmodel import Session

from app.infrastructure.database import engine
from app.modules.bookings.repository import BookingRepository
from app.modules.bookings.service import BookingService
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.safe_in_memory_card_store import SafeInMemoryCardStore
from app.modules.payments.service import PaymentService
from app.shared.event_bus import EventBus

SessionFactory = Callable[[], AbstractContextManager[Session]]
BookingServiceFactory = Callable[[], AbstractContextManager[BookingService]]
PaymentServiceFactory = Callable[[], AbstractContextManager[PaymentService]]


@contextmanager
def get_session_scope() -> Iterator[Session]:
    with Session(engine) as session:
        yield session


def build_booking_service_factory(
    session_factory: SessionFactory,
    event_bus: EventBus,
) -> BookingServiceFactory:
    @contextmanager
    def factory() -> Iterator[BookingService]:
        with session_factory() as session:
            yield BookingService(BookingRepository(session), event_bus)

    return factory


def build_payment_service_factory(
    session_factory: SessionFactory,
    event_bus: EventBus,
    card_store: SafeInMemoryCardStore,
) -> PaymentServiceFactory:
    @contextmanager
    def factory() -> Iterator[PaymentService]:
        with session_factory() as session:
            yield PaymentService(
                card_store,
                PaymentRepository(session),
                BookingRepository(session),
                event_bus,
            )

    return factory