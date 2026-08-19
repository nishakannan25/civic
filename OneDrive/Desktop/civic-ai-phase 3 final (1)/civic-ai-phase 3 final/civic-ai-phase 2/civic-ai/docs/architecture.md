# Civic AI - Architecture Specification

## 1. System Overview

**Civic AI** is an intelligent, edge-first civic problem reporting and community emergency response platform. The architecture is designed to handle civic issue reporting (potholes, open manholes, garbage, flooding), verify reports through decentralized community consensus, dynamically evaluate civic risks, and route actionable tasks to municipal authorities or emergency responders.

```
┌────────────────────────────────────────────────────────┐
│               Civic AI Client Ecosystem                │
│                                                        │
│  📱 Citizen Mobile App        💻 Admin & Responder Web │
│    (Flutter - iOS/Android)      (React / TypeScript)   │
└───────────────────┬───────────────────────┬────────────┘
                    │                       │
                    │ REST / Multipart      │ REST / WebSocket
                    ▼                       ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI API Gateway                    │
│                                                        │
│  - Authentication & JWT RBAC (Citizen, Responder, Admin)│
│  - Incident Creation & Multipart Upload Handler       │
│  - Rate Limiting & Input Validation (Pydantic v2)     │
└───────┬───────────────────┬───────────────────┬────────┘
        │                   │                   │
        │ SQLAlchemy ORM    │ Async REST/gRPC   │ Push Alerts
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │  AI Vision   │    │ Push / Alert │
│   Database   │    │   Service    │    │ Dispatcher   │
│              │    │  (Phase 4/5) │    │  (Phase 8)   │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 2. Phase Implementation Roadmap & Status

### Phase 1 Implemented Foundation:
- **Mobile Foundation**: Flutter project (`com.civicai.app`) with camera-first viewport preview, large touch targets, accessible civic theme, and bottom navigation shell.
- **Backend Service**: FastAPI with async router architecture, centralized configuration management, JWT authentication with bcrypt password hashing, and full OpenAPI documentation.
- **Relational Data Layer**: PostgreSQL schema managed via SQLAlchemy 2.0 ORM models for Users, Incidents, Verifications, Notifications, Departments, Point Transactions, and SOS Events.
- **Container Infrastructure**: Docker & Docker Compose setup linking FastAPI backend and PostgreSQL with healthchecks.

### Phase 2 Implemented Architecture:
- **Live Mobile Camera Module**: `camera` plugin integration with runtime permissions, viewfinder overlay, instant capture, and image preview.
- **Citizen Perceived Severity Rating**: 0–10 integer scale input via interactive `SeveritySlider` widget.
- **Geolocation Module**: Single-fix GPS capture with `geolocator`, 10-second fallback, and support for `UNAVAILABLE` status without application crash.
- **Multipart Upload Pipeline**: HTTP multipart/form-data image upload to FastAPI backend with `StorageService` saving to local `/uploads/incidents/` directory.
- **Incident API & Data Schema**: `POST /incidents` accepting image binary, citizen rating (0–10), optional GPS coordinates, and returning slim response with reference ID (`CIV-YYYY-NNNNNN`).

### Phase 3 Implemented Architecture (Offline Storage & Sync):
- **Local Persistent Incident Database**: Persistent store on device surviving app restarts and crashes.
- **Persistent Image Storage**: Captured camera images copied to app storage (`local_storage/incidents/<local_id>/image.jpg`) before temp files are purged.
- **Real-Time Connectivity Monitoring**: Active health & socket verification detecting online/offline transitions.
- **FIFO Synchronization Queue**: Background sync queue uploading pending reports oldest-first automatically upon connection restore.
- **Exponential Backoff Strategy**: 2s base backoff ($2^n \times \text{initialBackoff}$, max 30s) across 4 retries before marking `FAILED`.
- **Backend Idempotency Protection**: `client_incident_id` and `uploaded_at` tracking; duplicate submissions return existing record without creating duplicate database rows.
- **Saved Reports UI**: Dedicated screen displaying local reports with sync badges and manual sync trigger.

### Future Phase Integrations:
1. **Phase 4 & 5**: AI Computer Vision Microservice running YOLO object detection and classification.
2. **Phase 6 & 7**: Geocoding and Risk Assessment Engine (fusing AI severity, citizen feedback, and geospatial proximity).
3. **Phase 8 & 9**: Push Notification engine and Citizen Gamification/Trust scoring system.
4. **Phase 10 & 11**: SOS Emergency dispatch router and Municipal Admin Dashboard.

---

## 3. Mobile Camera & Incident Creation Flow (Phase 2)

```
[ APP OPEN ]
     │
     ▼
┌────────────────────────┐
│  CameraScreen          │ ◄── Handles camera permissions (Granted / Denied / Permanently Denied)
│  [ LIVE PREVIEW ]      │     Displays live viewfinder with corner bracket overlay
└───────────┬────────────┘
            │ CAPTURE PROBLEM (Captures high-res JPEG locally)
            ▼
┌────────────────────────┐
│ IncidentPreviewScreen  │
│  [ IMAGE PREVIEW ]     │ ◄── User can RETAKE or inspect captured image
│  [ RATING 0 - 10 ]     │ ◄── Integer rating (default 5, green→orange→red slider)
└───────────┬────────────┘
            │ CONTINUE / SUBMIT INCIDENT
            ▼
┌────────────────────────┐
│  Location Capture      │ ◄── Single-fix GPS check (10s timeout)
│  (Service Layer)       │     If unavailable, sets location_status = "UNAVAILABLE" & coords = null
└───────────┬────────────┘
            │ Multipart POST /incidents
            ▼
┌────────────────────────┐
│  FastAPI Backend       │ ◄── Validates MIME (JPEG/PNG), size (≤10MB), rating (0–10)
│  & PostgreSQL          │     Saves file to uploads/incidents/, inserts Incident row with status CREATED
└───────────┬────────────┘
            │ Return 201 Created { id, reference_id, status }
            ▼
┌────────────────────────┐
│ IncidentSuccessScreen  │ ◄── Displays reference ID (CIV-2026-000123), summary & "Report Another" button
└────────────────────────┘
```

---

## 4. Technical Architecture Details (Phase 2 Specifications)

### 1. Camera Flow
- Primary entry point remains **Camera-First** upon opening app.
- Permission states:
  - **Granted**: Initialises back camera with `ResolutionPreset.high` and JPEG format.
  - **Denied**: Displays `CameraPermissionView` with "Grant Permission" action.
  - **Permanently Denied**: Displays `CameraPermissionView` with "Open Settings" action.
  - **Init Failure**: Shows user-friendly error with "Retry" button (app does not crash).

### 2. Citizen Severity Rating
- Rating range: **0 to 10** (integer). Default value: `5`.
- Label: *"How serious is this problem for you?"*
- Representing **Citizen Perceived Severity** ONLY (kept completely separate from AI confidence, AI severity, or risk engine scores).

### 3. GPS Handling
- Captures `latitude`, `longitude`, `accuracy` (metres), and `timestamp`.
- Permission handling: Request location permission only during incident creation flow (privacy-by-design, no continuous background tracking).
- Unavailable GPS handling:
  - If GPS is disabled, denied, or times out (>10 seconds), application sets `location_status = "UNAVAILABLE"` and `latitude = null`, `longitude = null`, `gps_accuracy = null`.
  - Application does **NOT** invent fake coordinates or crash.

### 4. Image Upload & Storage Service
- Upload method: `multipart/form-data` with `http.MultipartFile` under form key `image`.
- Backend `StorageService`:
  - Validates image MIME (`image/jpeg`, `image/jpg`, `image/png`) and file size (≤ 10 MB).
  - Generates UUID-based unique filename (`uploads/incidents/<uuid>.<ext>`).
  - Served via FastAPI `StaticFiles` mount at `/uploads`.
  - Swappable interface ready for S3 / Cloud Storage providers in production.

### 5. Backend Database Schema (Incidents Table)

| Field Name | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | Primary Key, Auto-increment | Unique incident ID |
| `user_id` | Integer | Foreign Key (`users.id`), NOT NULL | Reporter user ID |
| `image_url` | String(512) | Nullable | Path to stored image |
| `latitude` | Float | Nullable (Phase 2 change) | Decimal latitude degrees |
| `longitude` | Float | Nullable (Phase 2 change) | Decimal longitude degrees |
| `gps_accuracy` | Float | Nullable | GPS precision in metres |
| `location_status` | String(20) | NOT NULL, default `"UNAVAILABLE"` | `AVAILABLE` or `UNAVAILABLE` |
| `timestamp` | DateTime | NOT NULL | Mobile device or server time |
| `citizen_rating` | Integer | Nullable, 0–10 | Citizen perceived severity |
| `status` | String(50) | NOT NULL, default `"CREATED"` | Current lifecycle state |
| `created_at` | DateTime | NOT NULL | Record creation timestamp |
| `updated_at` | DateTime | Nullable | Last record update timestamp |

### 6. Incident Status Lifecycle Machine

```
   [ Citizen Capture ]
           │
           ▼
        [ DRAFT ] ──────────► [ PENDING_SYNC ] (Phase 3 Offline Queue)
           │                          │
           ▼                          ▼
       [ CREATED ] (Phase 2 Direct Submit)
           │
           ▼
   [ AI_PROCESSING ] (Phase 4 YOLO Vision)
           │
           ▼
[ COMMUNITY_VERIFICATION ] (Phase 5 Consensus)
           │
           ▼
    [ RISK_ASSESSED ] (Phase 7 Risk Engine)
           │
           ▼
   [ ACTION_REQUIRED ] ──► [ RESOLVED ] ──► [ CLOSED ]
```

### 7. Error Handling Matrix

| Error Scenario | Component | Action / UI Response |
|---|---|---|
| Camera permission denied | Mobile UI | Displays `CameraPermissionView` with retry option |
| Camera init failure | Mobile UI | Shows "Unable to start camera. Please try again." |
| Image capture failure | Mobile UI | SnackBar notification: "Could not capture image. Please try again." |
| Location service disabled / denied | Mobile UI / GPS | Sets `location_status = UNAVAILABLE`, continues without coords |
| GPS timeout (>10s) | Mobile GPS | Falls back to lower accuracy; if still timeout, sets `location_status = UNAVAILABLE` |
| Network unavailable | Mobile Net | Displays: "Unable to submit right now. Your report could not be uploaded." |
| Invalid image type | FastAPI API | Returns `400 Bad Request` with `{"detail": "Unsupported image format..."}` |
| Oversized image (>10MB) | FastAPI API | Returns `400 Bad Request` with `{"detail": "Image file too large..."}` |
| Unauthenticated submission | FastAPI Security | Returns `401 Unauthorized` |
| Database error | FastAPI DB | Returns `500 Internal Server Error` with sanitized message |

---

## 5. Phase 2 Limitations & Phase 3 Extension Plan

### Phase 2 Limitations:
1. **Network Requirement**: Submissions require active internet connection. If offline, submission fails with an explicit user error.
2. **No Local Persistence**: Failed submissions are not saved locally on device.
3. **No Automatic Retry**: Retries must be initiated manually by tapping Submit again.

### How Phase 3 Will Extend the System:
1. **Local SQLite Database**: Will store drafted incidents locally when offline with status `DRAFT`.
2. **Pending Sync Queue**: Incidents created without internet will be placed in `PENDING_SYNC` queue.
3. **Background Sync Engine**: Will automatically detect connectivity restoration and upload pending incidents with media in the background.
4. **GPS Retry Queue**: If location was `UNAVAILABLE` during capture, Phase 3 background worker can attempt GPS re-acquisition before final sync.

---

## 6. Phase 6 Architecture: Risk Engine & Assessment

### Overview:
Phase 6 introduces the Risk Engine (`RiskEngineService`), transforming Phase 5 AI vision results, citizen-reported rating, and GPS location availability into a normalized risk score (0–100), categorical risk level, priority classification, and deterministic rule-based explanation.

### Risk Scoring Formula:
$$\text{Risk Score} = \text{clamp}\left(100 \times \left( \frac{\text{Severity}}{100} \cdot W_{\text{sev}} + \text{Conf} \cdot W_{\text{conf}} + \frac{\text{Rating}}{10} \cdot W_{\text{rating}} + \text{Loc} \cdot W_{\text{loc}} \right), 0, 100\right)$$

- Default weights: $W_{\text{sev}} = 0.40$, $W_{\text{conf}} = 0.30$, $W_{\text{rating}} = 0.20$, $W_{\text{loc}} = 0.10$.
- Baseline severities: Open Manhole (95), Flooding (90), Pothole (70), Water Leakage (60), Broken Streetlight (50), Garbage (40).
- Categorical Levels: LOW (<25), MEDIUM (<50), HIGH (<75), CRITICAL (≥75).
- Priority Mapping: LOW → LOW, MEDIUM → NORMAL, HIGH → HIGH, CRITICAL → URGENT.

### Database Schema (`risk_assessments` table):
- `id`: PK
- `incident_id`: FK (`incidents.id`), UNIQUE constraint for 1:1 relation (upsert semantics).
- `risk_score`: Float (0–100).
- `risk_level`: String (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- `priority`: String (`LOW`, `NORMAL`, `HIGH`, `URGENT`).
- `crisis_class`, `crisis_severity`, `ai_confidence`, `citizen_rating`, `location_available`: Input snapshot.
- `explanation`: Deterministic human-readable string.
- `calculated_at`: Timestamp UTC.

