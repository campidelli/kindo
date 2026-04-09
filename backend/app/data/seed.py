"""Seed the database with a sample trip.

Run from the backend/ directory:

    .venv/bin/python -m app.data.seed
"""
from datetime import datetime, timezone

from sqlmodel import Session, SQLModel, select

from app.core.database import engine
from app.models import Trip

def main() -> None:
    SQLModel.metadata.create_all(engine)

    trips = [
        Trip(
            title="Wellington Zoo Field Trip",
            description=(
                "An exciting visit to Wellington Zoo where students will learn "
                "about native New Zealand wildlife and conservation efforts."
            ),
            date=datetime(2026, 6, 15),
            location="Wellington Zoo, 200 Daniell St, Newtown, Wellington",
            cost=35.00,
            school_id="SCH-001",
            activity_id="ACT-ZOO-2026",
        ),
        Trip(
            title="Auckland Aquarium Field Trip",
            description=(
                "A fascinating journey through Kelly Tarlton's Sea Life Aquarium, "
                "exploring Antarctic penguins, sharks, and the diverse marine life "
                "of the Pacific Ocean."
            ),
            date=datetime(2026, 7, 22),
            location="Kelly Tarlton's Sea Life Aquarium, 23 Tamaki Dr, Auckland",
            cost=42.00,
            school_id="SCH-001",
            activity_id="ACT-AQU-2026",
        ),
    ]

    with Session(engine) as session:
        for trip in trips:
            exists = session.exec(
                select(Trip).where(Trip.activity_id == trip.activity_id)
            ).first()
            if not exists:
                session.add(trip)
                print(f"Seeded trip: {trip.title}")
            else:
                print(f"Trip already exists - skipping: {trip.title}")
        session.commit()


if __name__ == "__main__":
    main()
