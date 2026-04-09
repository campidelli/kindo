"""Integration tests for the full API flow."""
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.database import get_session
from app.core.logging import configure_logging
from app.enums.payment_status import PaymentStatus
from app.integrations.legacy_payment_processor import PaymentResponse
from app.models import Payment, Trip


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a TestClient with the test database."""
    configure_logging()
    
    def get_session_override():
        return session

    test_app = FastAPI(title="Test App", version="1.0.0")
    test_app.dependency_overrides[get_session] = get_session_override
    
    from app.routers import trips, payments
    test_app.include_router(trips.router)
    test_app.include_router(payments.router)
    
    return TestClient(test_app)


class TestTripEndpoints:
    def test_list_trips_empty(self, client: TestClient):
        """GET /api/v1/trips with no trips."""
        response = client.get("/api/v1/trips")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_trips_with_data(self, session: Session, client: TestClient):
        """GET /api/v1/trips with trips in the database."""
        trip1 = Trip(
            title="Zoo Trip",
            description="Learn about animals",
            date=datetime(2026, 6, 15),
            location="Wellington Zoo",
            cost=35.00,
            school_id="SCH-001",
            activity_id="ACT-ZOO",
        )
        trip2 = Trip(
            title="Museum Trip",
            description="Learn about history",
            date=datetime(2026, 7, 20),
            location="Te Papa Museum",
            cost=25.00,
            school_id="SCH-001",
            activity_id="ACT-MUS",
        )
        session.add(trip1)
        session.add(trip2)
        session.commit()

        response = client.get("/api/v1/trips")
        assert response.status_code == 200
        trips = response.json()
        assert len(trips) == 2
        assert trips[0]["title"] == "Zoo Trip"
        assert trips[1]["title"] == "Museum Trip"

    def test_get_trip_by_id(self, session: Session, client: TestClient):
        """GET /api/v1/trips/{trip_id}."""
        trip = Trip(
            title="Zoo Trip",
            description="Learn about animals",
            date=datetime(2026, 6, 15),
            location="Wellington Zoo",
            cost=35.00,
            school_id="SCH-001",
            activity_id="ACT-ZOO",
        )
        session.add(trip)
        session.commit()

        response = client.get(f"/api/v1/trips/{trip.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(trip.id)
        assert data["title"] == "Zoo Trip"
        assert data["cost"] == 35.00

    def test_get_trip_not_found(self, client: TestClient):
        """GET /api/v1/trips/{trip_id} with non-existent trip."""
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/trips/{fake_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Trip not found."


class TestPaymentEndpoints:
    @pytest.fixture
    def trip(self, session: Session):
        """Create a sample trip for payment tests."""
        trip = Trip(
            title="Zoo Trip",
            description="Learn about animals",
            date=datetime(2026, 6, 15),
            location="Wellington Zoo",
            cost=35.00,
            school_id="SCH-001",
            activity_id="ACT-ZOO",
        )
        session.add(trip)
        session.commit()
        return trip

    def test_create_payment_returns_201_with_pending(self, trip: Trip, client: TestClient):
        """POST /api/v1/payments returns 201 with PENDING status."""
        with patch("app.services.payment_service._processor.process_payment") as mock_processor:
            mock_processor.return_value = PaymentResponse(success=True, transaction_id="TXN-123")
            
            response = client.post(
                "/api/v1/payments",
                json={
                    "trip_id": str(trip.id),
                    "student_name": "Alice Smith",
                    "parent_name": "Bob Smith",
                    "card_number": "4111 1111 1111 1111",
                    "expiry_date": "12/30",
                    "cvv": "123",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == PaymentStatus.PENDING.value
        assert data["trip_id"] == str(trip.id)
        assert "payment_id" in data
        assert "created_at" in data

    def test_get_payment_by_id(self, trip: Trip, session: Session, client: TestClient):
        """GET /api/v1/payments/{payment_id}."""
        payment = Payment(
            trip_id=trip.id,
            student_name="Alice Smith",
            parent_name="Bob Smith",
            card_last_four="1111",
            status=PaymentStatus.PENDING,
        )
        session.add(payment)
        session.commit()

        response = client.get(f"/api/v1/payments/{payment.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(payment.id)
        assert data["student_name"] == "Alice Smith"
        assert data["status"] == PaymentStatus.PENDING.value

    def test_get_payment_not_found(self, client: TestClient):
        """GET /api/v1/payments/{payment_id} with non-existent payment."""
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/payments/{fake_id}")
        assert response.status_code == 404

    def test_create_payment_fails_when_trip_not_found(self, client: TestClient):
        """POST /api/v1/payments with non-existent trip returns 404."""
        with patch("app.services.payment_service._processor.process_payment"):
            fake_trip_id = uuid.uuid4()
            response = client.post(
                "/api/v1/payments",
                json={
                    "trip_id": str(fake_trip_id),
                    "student_name": "Alice Smith",
                    "parent_name": "Bob Smith",
                    "card_number": "4111 1111 1111 1111",
                    "expiry_date": "12/30",
                    "cvv": "123",
                },
            )

        assert response.status_code == 404
        assert response.json()["detail"] == "Trip not found."

    def test_payment_validation_card_number(self, trip: Trip, client: TestClient):
        """POST /api/v1/payments validates card number format."""
        response = client.post(
            "/api/v1/payments",
            json={
                "trip_id": str(trip.id),
                "student_name": "Alice Smith",
                "parent_name": "Bob Smith",
                "card_number": "123",
                "expiry_date": "12/30",
                "cvv": "123",
            },
        )
        assert response.status_code == 422

    def test_payment_validation_expiry_date(self, trip: Trip, client: TestClient):
        """POST /api/v1/payments validates expiry date format."""
        response = client.post(
            "/api/v1/payments",
            json={
                "trip_id": str(trip.id),
                "student_name": "Alice Smith",
                "parent_name": "Bob Smith",
                "card_number": "4111111111111111",
                "expiry_date": "2030",
                "cvv": "123",
            },
        )
        assert response.status_code == 422

    def test_payment_validation_cvv(self, trip: Trip, client: TestClient):
        """POST /api/v1/payments validates CVV format."""
        response = client.post(
            "/api/v1/payments",
            json={
                "trip_id": str(trip.id),
                "student_name": "Alice Smith",
                "parent_name": "Bob Smith",
                "card_number": "4111111111111111",
                "expiry_date": "12/30",
                "cvv": "12",
            },
        )
        assert response.status_code == 422


class TestFullWorkflow:
    def test_end_to_end_trip_and_payment_flow(self, session: Session, client: TestClient):
        """Full workflow: create trip, list, get, create payment, get payment."""
        with patch("app.services.payment_service._processor.process_payment") as mock_processor:
            mock_processor.return_value = PaymentResponse(success=True, transaction_id="TXN-123")
            
            # 1. Create a trip
            trip = Trip(
                title="Zoo Trip",
                description="Learn about animals",
                date=datetime(2026, 6, 15),
                location="Wellington Zoo",
                cost=35.00,
                school_id="SCH-001",
                activity_id="ACT-ZOO",
            )
            session.add(trip)
            session.commit()

            # 2. List trips
            response = client.get("/api/v1/trips")
            assert response.status_code == 200
            assert len(response.json()) == 1

            # 3. Get the specific trip
            response = client.get(f"/api/v1/trips/{trip.id}")
            assert response.status_code == 200
            assert response.json()["title"] == "Zoo Trip"

            # 4. Create a payment
            response = client.post(
                "/api/v1/payments",
                json={
                    "trip_id": str(trip.id),
                    "student_name": "Alice Smith",
                    "parent_name": "Bob Smith",
                    "card_number": "4111 1111 1111 1111",
                    "expiry_date": "12/30",
                    "cvv": "123",
                },
            )
            assert response.status_code == 201
            payment_id = response.json()["payment_id"]
            assert response.json()["status"] == PaymentStatus.PENDING.value

            # 5. Get the payment
            response = client.get(f"/api/v1/payments/{payment_id}")
            assert response.status_code == 200
            assert response.json()["status"] == PaymentStatus.PENDING.value
            assert response.json()["student_name"] == "Alice Smith"
