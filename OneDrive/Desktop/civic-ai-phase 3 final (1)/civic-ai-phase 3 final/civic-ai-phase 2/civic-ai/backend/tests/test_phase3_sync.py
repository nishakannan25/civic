"""Phase 3 Backend Tests: Idempotency, client_incident_id tracking, and offline sync compatibility.

Covers all Phase 3 backend verification criteria.
"""

import io
import pytest
from fastapi.testclient import TestClient


def _register_and_login(client: TestClient, email: str = "sync_user@example.com") -> dict:
    """Register a new user and return auth headers."""
    client.post("/auth/register", json={
        "name": "Sync Tester",
        "email": email,
        "password": "Password123!",
    })
    login_res = client.post("/auth/login", data={
        "username": email,
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _make_jpeg_file(size_bytes: int = 1024) -> bytes:
    """Return a minimal valid JPEG-like byte sequence."""
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + b"\x00" * max(0, size_bytes - 18)
        + b"\xff\xd9"
    )


def test_post_incident_with_client_incident_id(client: TestClient):
    """TEST 1: POST /incidents with client_incident_id succeeds and returns client_incident_id and uploaded_at."""
    headers = _register_and_login(client, "client_id_test@example.com")
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("test.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = {
        "citizen_rating": "6",
        "location_status": "AVAILABLE",
        "latitude": "12.9716",
        "longitude": "77.5946",
        "gps_accuracy": "4.2",
        "client_incident_id": "local-inc-uuid-001",
    }

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["id"] is not None
    assert body["client_incident_id"] == "local-inc-uuid-001"
    assert body["uploaded_at"] is not None
    assert body["message"] == "Incident created successfully"


def test_same_user_idempotent_duplicate_prevention(client: TestClient):
    """TEST 2 & TEST 7: Same user submitting the same client_incident_id twice returns existing incident without creating duplicates."""
    headers = _register_and_login(client, "idempotent_user@example.com")
    client_id = "local-inc-uuid-repeat-001"

    # First submission
    files1 = {"image": ("first.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
    data1 = {
        "citizen_rating": "8",
        "location_status": "AVAILABLE",
        "latitude": "13.0827",
        "longitude": "80.2707",
        "client_incident_id": client_id,
    }
    res1 = client.post("/incidents", data=data1, files=files1, headers=headers)
    assert res1.status_code == 201
    body1 = res1.json()
    first_server_id = body1["id"]
    assert body1["message"] == "Incident created successfully"

    # Second submission with same client_incident_id
    files2 = {"image": ("second.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
    data2 = {
        "citizen_rating": "8",
        "location_status": "AVAILABLE",
        "latitude": "13.0827",
        "longitude": "80.2707",
        "client_incident_id": client_id,
    }
    res2 = client.post("/incidents", data=data2, files=files2, headers=headers)
    assert res2.status_code == 201
    body2 = res2.json()
    assert body2["id"] == first_server_id
    assert body2["client_incident_id"] == client_id
    assert body2["message"] == "Incident already exists"

    # Verify count in database is still 1 for this incident
    list_res = client.get("/incidents", headers=headers)
    items = [it for it in list_res.json()["items"] if it.get("client_incident_id") == client_id]
    assert len(items) == 1


def test_different_users_with_different_client_incident_ids(client: TestClient):
    """TEST 3: Different users submit distinct client_incident_ids and both succeed."""
    headers_a = _register_and_login(client, "user_a@example.com")
    headers_b = _register_and_login(client, "user_b@example.com")

    files_a = {"image": ("a.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
    data_a = {
        "citizen_rating": "4",
        "location_status": "UNAVAILABLE",
        "client_incident_id": "client-id-user-a",
    }
    res_a = client.post("/incidents", data=data_a, files=files_a, headers=headers_a)
    assert res_a.status_code == 201
    assert res_a.json()["client_incident_id"] == "client-id-user-a"

    files_b = {"image": ("b.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
    data_b = {
        "citizen_rating": "5",
        "location_status": "UNAVAILABLE",
        "client_incident_id": "client-id-user-b",
    }
    res_b = client.post("/incidents", data=data_b, files=files_b, headers=headers_b)
    assert res_b.status_code == 201
    assert res_b.json()["client_incident_id"] == "client-id-user-b"
    assert res_a.json()["id"] != res_b.json()["id"]


def test_idempotency_key_header_support(client: TestClient):
    """TEST 4: Idempotency-Key header is accepted and recognized as client_incident_id."""
    headers = _register_and_login(client, "header_user@example.com")
    headers["Idempotency-Key"] = "idemp-header-999"

    files = {"image": ("header.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
    data = {
        "citizen_rating": "5",
        "location_status": "UNAVAILABLE",
    }
    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 201
    body = res.json()
    assert body["client_incident_id"] == "idemp-header-999"

    # Repeat with same header
    files2 = {"image": ("header2.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
    res2 = client.post("/incidents", data=data, files=files2, headers=headers)
    assert res2.status_code == 201
    assert res2.json()["id"] == body["id"]
    assert res2.json()["message"] == "Incident already exists"


def test_offline_sync_gps_unavailable_with_client_id(client: TestClient):
    """TEST 5: Offline report synced later without GPS coordinates preserves location_status=UNAVAILABLE."""
    headers = _register_and_login(client, "offline_sync_nogps@example.com")
    files = {"image": ("offline.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
    data = {
        "citizen_rating": "9",
        "location_status": "UNAVAILABLE",
        "timestamp": "2026-08-17T03:15:00Z",
        "client_incident_id": "offline-nogps-777",
    }
    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 201
    body = res.json()
    assert body["location_status"] == "UNAVAILABLE"
    assert body["latitude"] is None
    assert body["longitude"] is None
    assert body["client_incident_id"] == "offline-nogps-777"


def test_database_level_unique_constraint(db_session):
    """TEST 6: Database-level UniqueConstraint on (user_id, client_incident_id) raises IntegrityError on duplicate insert."""
    from sqlalchemy.exc import IntegrityError
    from app.models.user import User
    from app.models.incident import Incident

    user = User(name="DB Constraint User", email="unique_constraint@example.com", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    inc1 = Incident(user_id=user.id, client_incident_id="dup-db-check-001", citizen_rating=5, location_status="UNAVAILABLE")
    db_session.add(inc1)
    db_session.commit()

    inc2 = Incident(user_id=user.id, client_incident_id="dup-db-check-001", citizen_rating=7, location_status="UNAVAILABLE")
    db_session.add(inc2)

    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
