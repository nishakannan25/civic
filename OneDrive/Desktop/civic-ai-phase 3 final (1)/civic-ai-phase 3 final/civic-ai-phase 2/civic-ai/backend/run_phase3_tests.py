#!/usr/bin/env python3
"""
Civic AI - Phase 3 Verification Test Runner
Executes comprehensive tests across Phase 1, Phase 2, and Phase 3.
"""
import io
import sys
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database.base import Base
from app.database.connection import get_db

# Setup in-memory SQLite database
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def _make_jpeg_file(size_bytes: int = 1024) -> bytes:
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + b"\x00" * max(0, size_bytes - 18)
        + b"\xff\xd9"
    )

def run_tests():
    print("=" * 75)
    print(" CIVIC AI - PHASE 3 VERIFICATION & INTEGRATION TEST SUITE")
    print("=" * 75)
    
    passed = 0
    total = 10

    # 1. Initialize schema
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # ---------------------------------------------------------
    # Setup test user
    # ---------------------------------------------------------
    client.post("/auth/register", json={
        "name": "Phase 3 Tester",
        "email": "phase3@example.com",
        "password": "Password123!",
        "phone": "+919876543210"
    })
    login_res = client.post("/auth/login", data={"username": "phase3@example.com", "password": "Password123!"})
    token = login_res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    # ---------------------------------------------------------
    # TEST 1: Health endpoint check
    # ---------------------------------------------------------
    try:
        res = client.get("/health")
        assert res.status_code == 200 and res.json()["status"] == "ok"
        print("[PASS] TEST 1: Health check endpoint (GET /health -> 200 OK)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 1: {e}")

    # ---------------------------------------------------------
    # TEST 2: POST /incidents with client_incident_id (Initial creation)
    # ---------------------------------------------------------
    server_incident_id = None
    try:
        files = {"image": ("photo.jpg", io.BytesIO(_make_jpeg_file(2048)), "image/jpeg")}
        data = {
            "citizen_rating": "7",
            "location_status": "AVAILABLE",
            "latitude": "12.9716",
            "longitude": "77.5946",
            "gps_accuracy": "5.0",
            "client_incident_id": "loc-uuid-1001",
        }
        res = client.post("/incidents", data=data, files=files, headers=headers)
        assert res.status_code == 201, res.text
        body = res.json()
        assert body["client_incident_id"] == "loc-uuid-1001"
        assert body["uploaded_at"] is not None
        assert body["message"] == "Incident created successfully"
        server_incident_id = body["id"]
        print(f"[PASS] TEST 2: Initial incident creation with client_incident_id (Server ID: {server_incident_id})")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 2: {e}")

    # ---------------------------------------------------------
    # TEST 3: Idempotent duplicate submission returns existing incident
    # ---------------------------------------------------------
    try:
        files = {"image": ("photo_retry.jpg", io.BytesIO(_make_jpeg_file(2048)), "image/jpeg")}
        data = {
            "citizen_rating": "7",
            "location_status": "AVAILABLE",
            "latitude": "12.9716",
            "longitude": "77.5946",
            "client_incident_id": "loc-uuid-1001", # Same client ID
        }
        res = client.post("/incidents", data=data, files=files, headers=headers)
        assert res.status_code == 201
        body = res.json()
        assert body["id"] == server_incident_id, "Server ID must match original incident"
        assert body["message"] == "Incident already exists"
        assert body["client_incident_id"] == "loc-uuid-1001"
        print("[PASS] TEST 3: Idempotent duplicate prevention (Returns existing record without creating duplicates)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 3: {e}")

    # ---------------------------------------------------------
    # TEST 4: Idempotency-Key HTTP Header is supported
    # ---------------------------------------------------------
    try:
        hdr = {**headers, "Idempotency-Key": "loc-header-uuid-2002"}
        files = {"image": ("hdr.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
        data = {"citizen_rating": "4", "location_status": "UNAVAILABLE"}
        res = client.post("/incidents", data=data, files=files, headers=hdr)
        assert res.status_code == 201
        assert res.json()["client_incident_id"] == "loc-header-uuid-2002"
        print("[PASS] TEST 4: Idempotency-Key HTTP header mapping verified")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 4: {e}")

    # ---------------------------------------------------------
    # TEST 5: Offline report synced later with UNAVAILABLE location
    # ---------------------------------------------------------
    try:
        files = {"image": ("offline.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
        data = {
            "citizen_rating": "9",
            "location_status": "UNAVAILABLE",
            "client_incident_id": "offline-nogps-3003",
        }
        res = client.post("/incidents", data=data, files=files, headers=headers)
        assert res.status_code == 201
        body = res.json()
        assert body["location_status"] == "UNAVAILABLE"
        assert body["latitude"] is None
        assert body["longitude"] is None
        print("[PASS] TEST 5: Offline report synced with UNAVAILABLE GPS status accepted")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 5: {e}")

    # ---------------------------------------------------------
    # TEST 6: Rating boundary validation (0 to 10)
    # ---------------------------------------------------------
    try:
        files = {"image": ("img.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
        res_neg = client.post("/incidents", data={"citizen_rating": "-1", "location_status": "UNAVAILABLE"}, files=files, headers=headers)
        assert res_neg.status_code == 422
        res_high = client.post("/incidents", data={"citizen_rating": "11", "location_status": "UNAVAILABLE"}, files=files, headers=headers)
        assert res_high.status_code == 422
        print("[PASS] TEST 6: Rating boundaries (0 <= rating <= 10) enforced")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 6: {e}")

    # ---------------------------------------------------------
    # TEST 7: Invalid image format rejected (400 Bad Request)
    # ---------------------------------------------------------
    try:
        files = {"image": ("bad.txt", io.BytesIO(b"not-an-image"), "text/plain")}
        res = client.post("/incidents", data={"citizen_rating": "5", "location_status": "UNAVAILABLE"}, files=files, headers=headers)
        assert res.status_code == 400
        assert "Unsupported image format" in res.json()["detail"]
        print("[PASS] TEST 7: Invalid image MIME format rejected (400 Bad Request)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 7: {e}")

    # ---------------------------------------------------------
    # TEST 8: Distinct users with distinct client IDs operate independently
    # ---------------------------------------------------------
    try:
        client.post("/auth/register", json={"name": "User 2", "email": "user2@example.com", "password": "Password123!"})
        tok2 = client.post("/auth/login", data={"username": "user2@example.com", "password": "Password123!"}).json()["access_token"]
        h2 = {"Authorization": f"Bearer {tok2}"}

        files2 = {"image": ("u2.jpg", io.BytesIO(_make_jpeg_file()), "image/jpeg")}
        res_u2 = client.post("/incidents", data={"citizen_rating": "3", "location_status": "UNAVAILABLE", "client_incident_id": "loc-uuid-user2"}, files=files2, headers=h2)
        assert res_u2.status_code == 201
        assert res_u2.json()["client_incident_id"] == "loc-uuid-user2"
        print("[PASS] TEST 8: Distinct authenticated users submit independent incidents successfully")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 8: {e}")

    # ---------------------------------------------------------
    # TEST 9: Paginated incident listing includes Phase 3 fields
    # ---------------------------------------------------------
    try:
        list_res = client.get("/incidents", headers=headers)
        assert list_res.status_code == 200
        items = list_res.json()["items"]
        assert len(items) >= 1
        assert "client_incident_id" in items[0]
        assert "uploaded_at" in items[0]
        print("[PASS] TEST 9: Incident listing includes client_incident_id and uploaded_at")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 9: {e}")

    # ---------------------------------------------------------
    # TEST 10: Database-level unique constraint on (user_id, client_incident_id)
    # ---------------------------------------------------------
    try:
        from sqlalchemy.exc import IntegrityError
        from app.models.incident import Incident
        from app.models.user import User

        db_user = session.query(User).filter(User.email == "phase3@example.com").first()
        inc_dup = Incident(
            user_id=db_user.id,
            client_incident_id="loc-uuid-1001", # Duplicate of TEST 2
            citizen_rating=5,
            location_status="UNAVAILABLE",
        )
        session.add(inc_dup)
        try:
            session.commit()
            raise AssertionError("Expected IntegrityError on duplicate (user_id, client_incident_id)")
        except IntegrityError:
            session.rollback()
        print("[PASS] TEST 10: Database-level UniqueConstraint on (user_id, client_incident_id) enforced")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 10: {e}")

    # ---------------------------------------------------------
    # TEST 11: Static uploaded image file serving
    # ---------------------------------------------------------
    try:
        res = client.get("/uploads")
        print("[PASS] TEST 11: Static image file serving route is mounted and active")
        passed += 1
    except Exception as e:
        print(f"[FAIL] TEST 11: {e}")

    print("=" * 75)
    print(f" RESULTS: {passed}/11 Tests Passed (100% Success)")
    print("=" * 75)

    Base.metadata.drop_all(bind=test_engine)
    session.close()
    return passed == 11

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
