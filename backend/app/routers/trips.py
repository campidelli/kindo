import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.core.database import get_session
from app.repositories.trip_repository import TripRepository
from app.schemas import TripResponse
from app.services.trip_service import TripService

router = APIRouter(prefix="/api/v1/trips", tags=["trips"])

DbDep = Annotated[Session, Depends(get_session)]


def get_trip_service(db: DbDep) -> TripService:
    return TripService(TripRepository(db))


TripServiceDep = Annotated[TripService, Depends(get_trip_service)]


@router.get("", response_model=list[TripResponse])
def list_trips(service: TripServiceDep):
    return service.get_all()


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: uuid.UUID, service: TripServiceDep):
    trip = service.get_by_id(trip_id)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.")
    return trip
