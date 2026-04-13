from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.infrastructure.config import settings
from app.infrastructure.database import engine
from app.infrastructure.logging import configure_logging, get_logger
from app.modules.admin.router import router as admin_router
from app.modules.bookings.router import router as bookings_router
from app.modules.payments.router import router as payments_router
from app.modules.receipts import router as receipts_router
from app.modules.trips.router import router as trips_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    SQLModel.metadata.create_all(engine)
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