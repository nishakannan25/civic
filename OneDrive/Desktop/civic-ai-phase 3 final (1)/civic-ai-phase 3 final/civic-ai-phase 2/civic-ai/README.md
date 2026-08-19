# Civic AI — Intelligent Community Emergency & Civic Problem Reporting System

> **Phase 6 Complete** — Risk Engine & Incident Priority Assessment

[![Phase](https://img.shields.io/badge/Phase-6%20Complete-success)](docs/architecture.md)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%2B%20PostgreSQL-blue)](docs/api.md)
[![Mobile](https://img.shields.io/badge/Mobile-Flutter%203.x-blue)](mobile/)

---

## What is Civic AI?

Civic AI enables citizens to report civic problems (potholes, flooding, open manholes, garbage) using their smartphone camera even when completely offline. Reports are preserved in local storage, synchronized with the FastAPI backend, classified using AI (Phase 5), and evaluated by a deterministic Risk Engine (Phase 6) to assign a risk score (0–100), risk level (LOW/MEDIUM/HIGH/CRITICAL), and incident priority (LOW/NORMAL/HIGH/URGENT).

---

## Phase Status

| Phase | Feature | Status |
|---|---|---|
| Phase 1 | Project foundation, auth, DB schema, UI shell | ✅ Complete |
| Phase 2 | Camera + GPS + Citizen Rating + Incident creation | ✅ Complete |
| Phase 3 | Offline storage + Sync queue + Backoff retry + Idempotency | ✅ Complete |
| Phase 4 | Dataset cleaning, balancing & 6-class dataset inventory | ✅ Complete |
| Phase 5 | MobileNetV3 AI vision inference microservice (6 classes) | ✅ Complete |
| **Phase 6** | **Risk Engine, severity calculation, priority, explanations** | ✅ **Complete** |
| Phase 7+ | Community consensus, routing, alerts, admin dashboard | 🔜 Next Phases |


---

## Phase 3 — What's New

### Mobile (Flutter)
- **Offline-First Reporting** — Save incidents and camera photos persistently on device when offline.
- **Persistent Local Database** — Full local incident store supporting CRUD, sync status tracking, and error logging.
- **Image Safety** — Captured photos copied to persistent app storage; preserved across app restarts until confirmed upload.
- **Real-Time Connectivity Detection** — Monitors connection changes with active ping validation.
- **Automatic Sync Queue** — Background FIFO synchronization triggers automatically when connectivity returns.
- **Exponential Backoff & Retry** — Configurable retry strategy ($2^n \times \text{initialBackoff}$) protecting against network flakiness.
- **Saved Reports Screen** — Dedicated UI displaying pending/uploaded reports with a manual `[ SYNC NOW ]` trigger.
- **Clear UX Distinction** — Explicit distinction between "Saved on this device" and "Uploaded to server".

### Backend (FastAPI + PostgreSQL)
- **Client Idempotency (`client_incident_id`)** — Unique client identifier preventing duplicate records on retry.
- **Duplicate-Safe Response** — Repeated submissions of the same client ID return the existing record without creating duplicate database rows.
- **`uploaded_at` Tracking** — Preserves both original citizen creation timestamp and actual synchronization time.
- **`Idempotency-Key` Header Support** — Supports HTTP standard idempotency headers alongside multipart form fields.

---

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 14+ (or use SQLite for tests)
- Flutter 3.10+
- Android/iOS device or emulator

### 1 — Backend

```bash
cd backend
python -m pip install -r requirements.txt

# Create .env from example
copy .env.example .env
# Edit .env: set DATABASE_URL, JWT_SECRET

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API Docs: http://localhost:8000/docs

### 2 — Mobile

```bash
cd mobile
flutter pub get
flutter run
```

> **Android emulator**: backend URL defaults to `http://10.0.2.2:8000`
> **Physical device**: edit `AppConfig.apiBaseUrl` to your local IP

### 3 — Run Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

Expected: **17/18 pass** (1 pre-existing Phase 1 auth test failure unrelated to Phase 2)

### 4 — Run Mobile Tests

```bash
cd mobile
flutter test
```

Expected: **12/12 pass**

---

## Project Structure

```
civic-ai/
├── backend/
│   ├── app/
│   │   ├── api/           incidents.py   ← POST /incidents multipart
│   │   ├── core/          config, constants, security
│   │   ├── models/        incident.py    ← location_status added
│   │   ├── schemas/       incident.py    ← 0-10 rating, optional coords
│   │   └── services/
│   │       ├── incident_service.py       ← create_incident_with_image()
│   │       └── storage_service.py        ← image validation & storage [NEW]
│   ├── uploads/incidents/                ← uploaded images (gitignored)
│   └── tests/             test_incidents.py [12 Phase 2 tests]
│
├── mobile/
│   └── lib/
│       ├── app/           routes.dart, theme.dart
│       ├── core/
│       │   ├── config/    app_config.dart
│       │   ├── constants/ app_colors, app_strings
│       │   ├── errors/    exceptions.dart
│       │   └── network/   api_client.dart  ← postMultipart() added
│       └── features/
│           ├── camera/
│           │   └── presentation/
│           │       └── camera_screen.dart   ← real camera [REPLACED]
│           └── incidents/
│               ├── data/    incident_repository.dart [NEW]
│               ├── models/  incident_model.dart, location_data.dart [NEW]
│               ├── screens/ incident_preview_screen.dart [NEW]
│               │            incident_success_screen.dart [NEW]
│               ├── services/ location_service.dart [NEW]
│               └── widgets/  severity_slider.dart [NEW]
│                             camera_permission_view.dart [NEW]
└── docs/
    ├── architecture.md
    ├── api.md
    └── testing.md
```

---

## Citizen Reporting Flow

```
OPEN APP
   ↓
CameraScreen  — live preview, CAPTURE PROBLEM button
   ↓
IncidentPreviewScreen
   ├── Image preview + RETAKE option
   ├── 0–10 severity slider
   └── SUBMIT INCIDENT
         ↓
         [GPS capture — with 10s timeout]
         ↓
         [Multipart upload to POST /incidents]
         ↓
IncidentSuccessScreen — CIV-YYYY-NNNNNN reference ID
```

---

## Configuration

| Setting | Location | Default |
|---------|----------|---------|
| API base URL | `AppConfig.apiBaseUrl` | `http://10.0.2.2:8000` (Android emulator) |
| Upload dir | `UPLOAD_DIR` (.env) | `uploads` |
| Max image size | `MAX_IMAGE_SIZE_MB` (.env) | `10` |
| JWT secret | `JWT_SECRET` (.env) | ⚠️ Change in production |
| GPS timeout | `LocationService._locationTimeout` | 10 seconds |
| Upload timeout | `AppConfig.uploadTimeout` | 30 seconds |

---

## Phase 2 Limitations (Resolved in Phase 3)

- No offline queue: if network fails, the incident is lost
- No automatic retry for GPS or upload failures
- Auth token stored in memory only (not persisted across sessions)
- No incident history view on mobile

---

## Docs

- [Architecture](docs/architecture.md)
- [API Reference](docs/api.md)
- [Testing Guide](docs/testing.md)
