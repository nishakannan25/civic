# Civic AI - REST API Specifications (Phase 2 Updated)

Base URL: `http://localhost:8000/api/v1` (or root `/` for health and direct endpoints)

---

## 1. System Health

### `GET /health`
Verify that backend service is running.

- **Request**: No headers or body required.
- **Response `200 OK`**:
```json
{
  "status": "ok",
  "service": "civic-ai-backend"
}
```

---

## 2. Authentication

### `POST /auth/register`
Register a new citizen account.

- **Request Body**:
```json
{
  "name": "Jane Citizen",
  "email": "jane@example.com",
  "password": "SecurePassword123!",
  "phone": "+919876543210"
}
```
- **Response `201 Created`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "name": "Jane Citizen",
    "email": "jane@example.com",
    "phone": "+919876543210",
    "role": "citizen",
    "points": 0,
    "reputation_score": 5.0,
    "created_at": "2026-08-16T11:00:00Z"
  }
}
```
- **Error `409 Conflict`**: Email already registered.

---

### `POST /auth/login`
Authenticate citizen credentials and obtain a JWT access token.

- **Request Body (OAuth2 Form or JSON)**:
```
username=jane@example.com&password=SecurePassword123!
```
- **Response `200 OK`**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```
- **Error `401 Unauthorized`**: Invalid email or password.

---

## 3. Users

### `GET /users/me`
Retrieve authenticated user profile.

- **Headers**: `Authorization: Bearer <access_token>`
- **Response `200 OK`**:
```json
{
  "id": 1,
  "name": "Jane Citizen",
  "email": "jane@example.com",
  "phone": "+919876543210",
  "role": "citizen",
  "points": 0,
  "reputation_score": 5.0,
  "created_at": "2026-08-16T11:00:00Z"
}
```
- **Error `401 Unauthorized`**: Token missing, malformed, or expired.

---

## 4. Incidents (Phase 3 Updated)

### `POST /incidents`
Submit a new civic incident report with an uploaded photo, citizen rating, GPS location, and idempotency key.

- **Headers**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: multipart/form-data`
  - `Idempotency-Key` (string, optional): Unique client incident identifier for safe background retries.
- **Form Data Fields**:
  - `image` (file, required): Image file (JPEG or PNG, max 10 MB).
  - `citizen_rating` (integer, required): Citizen perceived severity from `0` (minor) to `10` (critical).
  - `location_status` (string, optional, default `"UNAVAILABLE"`): `"AVAILABLE"` or `"UNAVAILABLE"`.
  - `latitude` (float, optional): Latitude decimal degrees (required if `location_status` is `"AVAILABLE"`).
  - `longitude` (float, optional): Longitude decimal degrees (required if `location_status` is `"AVAILABLE"`).
  - `gps_accuracy` (float, optional): Precision in metres.
  - `timestamp` (string, optional): ISO 8601 device timestamp (e.g. `2026-08-16T10:30:00Z`).
  - `client_incident_id` (string, optional): Unique client-generated ID for offline synchronization idempotency.

#### Example Request (cURL):
```bash
curl -X POST "http://localhost:8000/incidents" \
  -H "Authorization: Bearer <token>" \
  -H "Idempotency-Key: loc-1723855800000-7" \
  -F "image=@pothole.jpg;type=image/jpeg" \
  -F "citizen_rating=7" \
  -F "location_status=AVAILABLE" \
  -F "latitude=11.123456" \
  -F "longitude=76.123456" \
  -F "gps_accuracy=8.5" \
  -F "client_incident_id=loc-1723855800000-7"
```

#### Response `201 Created` (Initial Creation):
```json
{
  "id": 123,
  "reference_id": "CIV-2026-000123",
  "status": "CREATED",
  "citizen_rating": 7,
  "latitude": 11.123456,
  "longitude": 76.123456,
  "location_status": "AVAILABLE",
  "client_incident_id": "loc-1723855800000-7",
  "uploaded_at": "2026-08-17T03:30:00Z",
  "message": "Incident created successfully"
}
```

#### Response `201 Created` (Idempotent Retry / Duplicate Prevention):
```json
{
  "id": 123,
  "reference_id": "CIV-2026-000123",
  "status": "CREATED",
  "citizen_rating": 7,
  "latitude": 11.123456,
  "longitude": 76.123456,
  "location_status": "AVAILABLE",
  "client_incident_id": "loc-1723855800000-7",
  "uploaded_at": "2026-08-17T03:30:00Z",
  "message": "Incident already exists"
}
```

#### Example GPS Unavailable Response `201 Created`:
```json
{
  "id": 124,
  "reference_id": "CIV-2026-000124",
  "status": "CREATED",
  "citizen_rating": 5,
  "latitude": null,
  "longitude": null,
  "location_status": "UNAVAILABLE",
  "message": "Incident created successfully"
}
```

#### Error Responses:
- **`400 Bad Request`**:
  - Unsupported image format: `{"detail": "Unsupported image format 'text/plain'. Supported: JPEG, PNG."}`
  - Oversized image: `{"detail": "Image file too large. Maximum allowed size is 10 MB."}`
- **`422 Unprocessable Entity`**:
  - Rating out of range (e.g. rating = 15 or -2).
  - `location_status = AVAILABLE` but latitude/longitude omitted.
- **`401 Unauthorized`**: Token missing or invalid.

---

### `GET /incidents`
Retrieve a paginated list of civic incidents.

- **Query Parameters**:
  - `skip` (default: 0)
  - `limit` (default: 50, max: 100)
  - `status` (optional, e.g. `CREATED`, `RESOLVED`)
  - `user_id` (optional, filter by reporter)
- **Response `200 OK`**:
```json
{
  "total": 1,
  "items": [
    {
      "id": 123,
      "user_id": 1,
      "image_url": "/uploads/incidents/a1b2c3d4.jpg",
      "latitude": 11.123456,
      "longitude": 76.123456,
      "gps_accuracy": 8.5,
      "location_status": "AVAILABLE",
      "timestamp": "2026-08-16T10:30:00Z",
      "citizen_rating": 7,
      "ai_issue_type": null,
      "ai_confidence": null,
      "ai_severity": null,
      "community_yes": 0,
      "community_no": 0,
      "community_unknown": 0,
      "risk_score": null,
      "risk_level": null,
      "status": "CREATED",
      "created_at": "2026-08-16T10:30:00Z",
      "updated_at": null
    }
  ]
}
```

---

### `GET /incidents/{id}`
Retrieve incident details by incident ID.

- **Response `200 OK`**: Full Incident object.
- **Error `404 Not Found`**: When incident ID does not exist.

---

### `PATCH /incidents/{id}`
Update fields on an existing incident report.

- **Headers**: `Authorization: Bearer <access_token>`
- **Request Body**:
```json
{
  "status": "ACTION_REQUIRED",
  "citizen_rating": 8
}
```
- **Response `200 OK`**: Updated Incident object.

---

## 6. Risk Engine & Assessment (Phase 6)

### `POST /incidents/{incident_id}/risk-assessment`
Calculate and store a deterministic risk assessment for an incident. Requires Phase 5 AI inference results (`ai_issue_type`, `ai_confidence`) to be present on the incident.

- **Headers**: `Authorization: Bearer <access_token>`
- **Response `200 OK`**:
```json
{
  "incident_id": 123,
  "risk_score": 86.4,
  "risk_level": "CRITICAL",
  "priority": "URGENT",
  "crisis_class": "open_manhole",
  "crisis_severity": 95.0,
  "ai_confidence": 0.94,
  "citizen_rating": 9,
  "location_available": true,
  "explanation": "This is a CRITICAL incident requiring immediate response. The detected category (Open Manhole) has a very high baseline severity (95/100). AI confidence is strong (94%). Citizen-reported severity is high (9/10). GPS location is available, aiding field response. Calculated risk score: 86.4/100.",
  "calculated_at": "2026-08-17T15:40:00Z"
}
```
- **Error `404 Not Found`**: Incident with specified ID does not exist.
- **Error `422 Unprocessable Entity`**: Incident missing AI inference result or invalid rating/confidence.
- **Error `401 Unauthorized`**: Token missing or invalid.

