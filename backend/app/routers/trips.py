import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_db
from app.models import Trip
from app.schemas import TripResponse

router = APIRouter(prefix="/api/v1/trips", tags=["trips"])

DbDep = Annotated[Session, Depends(get_db)]


@router.get("", response_model=list[TripResponse])
def list_trips(db: DbDep):
    return db.exec(select(Trip)).all()


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: uuid.UUID, db: DbDep):
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found.")
    return trip
