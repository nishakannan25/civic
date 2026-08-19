"""Phase 2 Backend Tests: POST /incidents (multipart), rating validation, GPS, image validation.

Covers all 11 acceptance criteria from the Phase 2 spec (§32 Backend Tests).
"""

import io
import pytest
from fastapi.testclient import TestClient


# ─────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────

def _register_and_login(client: TestClient, email: str = "reporter@example.com") -> dict:
    """Register a new user and return auth headers."""
    client.post("/auth/register", json={
        "name": "Reporter",
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
    """Return a minimal JPEG-like byte sequence for upload tests."""
    # Real minimal JPEG header + body
    return (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        + b"\x00" * max(0, size_bytes - 18)
        + b"\xff\xd9"
    )


def _incident_form(
    citizen_rating: int = 5,
    location_status: str = "AVAILABLE",
    latitude: float = 11.123456,
    longitude: float = 76.123456,
    gps_accuracy: float = 8.5,
) -> dict:
    return {
        "citizen_rating": str(citizen_rating),
        "location_status": location_status,
        "latitude": str(latitude),
        "longitude": str(longitude),
        "gps_accuracy": str(gps_accuracy),
    }


# ─────────────────────────────────────────────────────────────────
# TEST 1: POST /incidents succeeds
# ─────────────────────────────────────────────────────────────────

def test_create_incident_success(client: TestClient):
    """TEST 1: POST /incidents succeeds with valid image and form data."""
    headers = _register_and_login(client, "success@example.com")

    jpeg_bytes = _make_jpeg_file(2048)
    files = {"image": ("test.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = _incident_form(citizen_rating=7)

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 201, res.text

    body = res.json()
    assert body["id"] is not None
    assert body["status"] == "CREATED"
    assert body["citizen_rating"] == 7
    assert body["latitude"] == 11.123456
    assert body["longitude"] == 76.123456
    assert body["location_status"] == "AVAILABLE"
    assert "CIV-" in body["reference_id"]
    assert body["message"] == "Incident created successfully"


# ─────────────────────────────────────────────────────────────────
# TEST 2: Valid citizen_rating = 0 is accepted
# ─────────────────────────────────────────────────────────────────

def test_create_incident_rating_zero(client: TestClient):
    """TEST 2: rating=0 is valid (minimum boundary)."""
    headers = _register_and_login(client, "rating0@example.com")
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("img.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = _incident_form(citizen_rating=0)

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 201, res.text
    assert res.json()["citizen_rating"] == 0


# ─────────────────────────────────────────────────────────────────
# TEST 3: Valid citizen_rating = 10 is accepted
# ─────────────────────────────────────────────────────────────────

def test_create_incident_rating_ten(client: TestClient):
    """TEST 3: rating=10 is valid (maximum boundary)."""
    headers = _register_and_login(client, "rating10@example.com")
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("img.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = _incident_form(citizen_rating=10)

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 201, res.text
    assert res.json()["citizen_rating"] == 10


# ─────────────────────────────────────────────────────────────────
# TEST 4: citizen_rating below 0 is rejected
# ─────────────────────────────────────────────────────────────────

def test_create_incident_rating_negative(client: TestClient):
    """TEST 4: rating=-1 must be rejected."""
    headers = _register_and_login(client, "ratingneg@example.com")
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("img.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = {**_incident_form(), "citizen_rating": "-1"}

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 422, res.text


# ─────────────────────────────────────────────────────────────────
# TEST 5: citizen_rating above 10 is rejected
# ─────────────────────────────────────────────────────────────────

def test_create_incident_rating_above_max(client: TestClient):
    """TEST 5: rating=11 must be rejected."""
    headers = _register_and_login(client, "ratinghigh@example.com")
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("img.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = {**_incident_form(), "citizen_rating": "11"}

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 422, res.text


# ─────────────────────────────────────────────────────────────────
# TEST 6: Valid GPS coordinates are accepted
# ─────────────────────────────────────────────────────────────────

def test_create_incident_with_gps(client: TestClient):
    """TEST 6: Incident with GPS coordinates is accepted and stored correctly."""
    headers = _register_and_login(client, "gps@example.com")
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("img.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = _incident_form(latitude=12.9716, longitude=77.5946, gps_accuracy=5.0)

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["location_status"] == "AVAILABLE"
    assert body["latitude"] == 12.9716


# ─────────────────────────────────────────────────────────────────
# TEST 7: Missing coordinates with UNAVAILABLE status are accepted
# ─────────────────────────────────────────────────────────────────

def test_create_incident_gps_unavailable(client: TestClient):
    """TEST 7: location_status=UNAVAILABLE with null coords is valid."""
    headers = _register_and_login(client, "nogps@example.com")
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("img.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = {
        "citizen_rating": "5",
        "location_status": "UNAVAILABLE",
    }

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 201, res.text
    body = res.json()
    assert body["location_status"] == "UNAVAILABLE"
    assert body["latitude"] is None
    assert body["longitude"] is None


# ─────────────────────────────────────────────────────────────────
# TEST 8: Invalid image MIME type is rejected
# ─────────────────────────────────────────────────────────────────

def test_create_incident_invalid_image_type(client: TestClient):
    """TEST 8: Unsupported file type (text/plain) must return 400."""
    headers = _register_and_login(client, "badtype@example.com")
    files = {"image": ("bad.txt", io.BytesIO(b"not an image"), "text/plain")}
    data = _incident_form()

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 400, res.text
    assert "Unsupported image format" in res.json()["detail"]


# ─────────────────────────────────────────────────────────────────
# TEST 9: Oversized image is rejected
# ─────────────────────────────────────────────────────────────────

def test_create_incident_oversized_image(client: TestClient):
    """TEST 9: Image > 10 MB must return 400."""
    headers = _register_and_login(client, "bigimg@example.com")
    # 11 MB fake JPEG
    big_bytes = b"\xff\xd8\xff" + b"\x00" * (11 * 1024 * 1024)
    files = {"image": ("big.jpg", io.BytesIO(big_bytes), "image/jpeg")}
    data = _incident_form()

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 400, res.text
    assert "too large" in res.json()["detail"].lower()


# ─────────────────────────────────────────────────────────────────
# TEST 10: Unauthenticated request is rejected
# ─────────────────────────────────────────────────────────────────

def test_create_incident_unauthenticated(client: TestClient):
    """TEST 10: Request without Authorization header must return 401."""
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("img.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = _incident_form()

    res = client.post("/incidents", data=data, files=files)
    assert res.status_code == 401, res.text


# ─────────────────────────────────────────────────────────────────
# TEST 11: GET /incidents returns list
# ─────────────────────────────────────────────────────────────────

def test_list_incidents(client: TestClient):
    """TEST 11: GET /incidents returns paginated list after creating an incident."""
    headers = _register_and_login(client, "list@example.com")

    # Create one incident
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("img.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = _incident_form()
    client.post("/incidents", data=data, files=files, headers=headers)

    res = client.get("/incidents")
    assert res.status_code == 200
    body = res.json()
    assert body["total"] >= 1
    assert isinstance(body["items"], list)


# ─────────────────────────────────────────────────────────────────
# TEST 12: AVAILABLE status with missing coords is rejected
# ─────────────────────────────────────────────────────────────────

def test_create_incident_available_status_missing_coords(client: TestClient):
    """TEST 12: location_status=AVAILABLE but no coords must return 422."""
    headers = _register_and_login(client, "missingcoords@example.com")
    jpeg_bytes = _make_jpeg_file()
    files = {"image": ("img.jpg", io.BytesIO(jpeg_bytes), "image/jpeg")}
    data = {
        "citizen_rating": "5",
        "location_status": "AVAILABLE",
        # No lat/lon
    }

    res = client.post("/incidents", data=data, files=files, headers=headers)
    assert res.status_code == 422, res.text
