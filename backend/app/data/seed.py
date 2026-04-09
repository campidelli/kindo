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

    with Session(engine) as session:
        existing = session.exec(select(Trip)).first()
        if existing is None:
            sample = Trip(
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
            )
            session.add(sample)
            session.commit()
            print("Seeded sample trip.")
        else:
            print("Trips already exist - skipping seed.")


if __name__ == "__main__":
    main()
