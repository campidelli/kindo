import logging
from datetime import datetime

from sqlmodel import Session, SQLModel, select

from app.infrastructure.database import engine
from app.modules.trips.models import Trip

logger = logging.getLogger(__name__)


class AdminService:
    def seed_database(self) -> dict[str, str]:
        try:
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
                session.commit()

            return {"status": "seeded", "message": "Database seeded successfully"}
        except Exception as exc:
            logger.error(f"Seed failed: {exc}")
            return {"status": "error", "message": str(exc)}
