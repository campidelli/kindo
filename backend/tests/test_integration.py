import uuid
from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.modules.payments.legacy_payment_processor import PaymentResponse
from app.modules.payments.models import PaymentStatus
from tests.conftest import make_trip


class TestTripEndpoints:
    def test_list_trips_empty(self, client: TestClient):
        response = client.get("/api/v1/trips")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_trips_with_data(self, session: Session, client: TestClient):
        trip1 = make_trip(title="Zoo Trip", activity_id="ACT-ZOO")
        trip2 = make_trip(title="Museum Trip", activity_id="ACT-MUS", date=datetime(2026, 7, 20))
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
        trip = make_trip(title="Zoo Trip", activity_id="ACT-ZOO")
        session.add(trip)
        session.commit()

        response = client.get(f"/api/v1/trips/{trip.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(trip.id)
        assert data["title"] == "Zoo Trip"
        assert data["cost"] == 35.00

    def test_get_trip_not_found(self, client: TestClient):
        fake_id = uuid.uuid4()
        response = client.get(f"/api/v1/trips/{fake_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Trip not found."


class TestBookingAndPaymentFlow:
    def test_create_and_cancel_booking(self, session: Session, client: TestClient):
        trip = make_trip()
        session.add(trip)
        session.commit()
        create_response = client.post(
            "/api/v1/bookings",
            json={
                "trip_id": str(trip.id),
                "parent_name": "Bob Smith",
                "child_name": "Alice Smith",
            },
        )

        assert create_response.status_code == 201
        booking = create_response.json()
        assert booking["status"] == "PENDING_PAYMENT"

        cancel_response = client.delete(f"/api/v1/bookings/{booking['id']}")
        assert cancel_response.status_code == 200
        assert cancel_response.json()["status"] == "CANCELLED"

    def test_create_payment_confirms_booking_and_generates_receipt(self, session: Session, client: TestClient):
        trip = make_trip(cost=52.50, activity_id="ACT-REC")
        session.add(trip)
        session.commit()

        booking_response = client.post(
            "/api/v1/bookings",
            json={
                "trip_id": str(trip.id),
                "parent_name": "Bob Smith",
                "child_name": "Alice Smith",
            },
        )
        booking_id = booking_response.json()["id"]

        with patch(
            "app.modules.payments.service.payment_processor.process_payment",
            return_value=PaymentResponse(success=True, transaction_id="TXN-123"),
        ):
            payment_response = client.post(
                "/api/v1/payments",
                json={
                    "booking_id": booking_id,
                    "card_number": "4111111111111111",
                    "cvv": "123",
                    "expiry_month": 12,
                    "expiry_year": 2030,
                },
            )

        assert payment_response.status_code == 201
        payment_id = payment_response.json()["id"]

        payment_lookup = client.get(f"/api/v1/payments/{payment_id}")
        assert payment_lookup.status_code == 200
        payment_data = payment_lookup.json()
        assert payment_data["status"] == PaymentStatus.SUCCESS.value
        assert payment_data["transaction_id"] == "TXN-123"
        assert payment_data["card_last_four"] == "1111"

        booking_lookup = client.get(f"/api/v1/bookings/{booking_id}")
        assert booking_lookup.status_code == 200
        assert booking_lookup.json()["status"] == "CONFIRMED"

        receipt_response = client.get(f"/api/v1/receipts/bookings/{booking_id}")
        assert receipt_response.status_code == 200
        receipt = receipt_response.json()
        assert receipt["booking"]["id"] == booking_id
        assert receipt["trip"]["id"] == str(trip.id)
        assert receipt["payment"]["id"] == payment_id
        assert receipt["payment"]["status"] == PaymentStatus.SUCCESS.value

    def test_create_payment_returns_404_when_booking_missing(self, client: TestClient):
        response = client.post(
            "/api/v1/payments",
            json={
                "booking_id": str(uuid.uuid4()),
                "card_number": "4111111111111111",
                "cvv": "123",
                "expiry_month": 12,
                "expiry_year": 2030,
            },
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Booking not found."

    def test_create_payment_validates_card_fields(self, session: Session, client: TestClient):
        trip = make_trip()
        session.add(trip)
        session.commit()

        booking_response = client.post(
            "/api/v1/bookings",
            json={
                "trip_id": str(trip.id),
                "parent_name": "Bob Smith",
                "child_name": "Alice Smith",
            },
        )

        response = client.post(
            "/api/v1/payments",
            json={
                "booking_id": booking_response.json()["id"],
                "card_number": "123",
                "cvv": "12",
                "expiry_month": 12,
                "expiry_year": 2,
            },
        )

        assert response.status_code == 422
