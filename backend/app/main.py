from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session

from app.infrastructure.config import settings
from app.infrastructure.database import engine
from app.infrastructure.logging import configure_logging, get_logger
from app.modules.admin.router import router as admin_router
from app.modules.bookings.handlers import BookingEventHandlers
from app.modules.bookings.repository import BookingRepository
from app.modules.bookings.router import router as bookings_router
from app.modules.bookings.service import BookingService
from app.modules.payments.handlers import PaymentEventHandlers
from app.modules.payments.repository import PaymentRepository
from app.modules.payments.router import router as payments_router
from app.modules.payments.safe_in_memory_card_store import get_card_store
from app.modules.payments.service import PaymentService
from app.modules.receipts import router as receipts_router
from app.modules.trips.router import router as trips_router
from app.shared.event_bus import get_event_bus

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    SQLModel.metadata.create_all(engine)
    event_bus = get_event_bus()
    event_bus.reset()
    with Session(engine) as session:
        booking_service = BookingService(BookingRepository(session), event_bus)
        payment_service = PaymentService(
            get_card_store(),
            PaymentRepository(session),
            BookingRepository(session),
            event_bus,
        )
        BookingEventHandlers(booking_service, event_bus).register_handlers()
        PaymentEventHandlers(payment_service, event_bus).register_handlers()
    logger.info("Database ready at %s", settings.database_path)
    yield
    logger.info("Shutting down")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trips_router)
app.include_router(bookings_router)
app.include_router(payments_router)
app.include_router(receipts_router)
app.include_router(admin_router)