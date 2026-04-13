from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from app.core.config import settings
from app.core.database import engine
from app.core.logging import configure_logging, get_logger
from app.modules.receipts import router as receipts_router
from app.routers import admin, payments, trips

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

app.include_router(trips.router)
app.include_router(payments.router)
app.include_router(receipts_router)
app.include_router(admin.router)