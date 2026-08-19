# Civic AI — Offline Storage & Synchronization Architecture (Phase 3)

## 1. Overview
Phase 3 introduces an **offline-first reliability layer** to Civic AI. When citizens report civic issues in areas with poor or absent network connectivity, their reports and captured photos are safely stored and encrypted in application-managed local storage. As soon as network connectivity is restored, the synchronization queue automatically uploads all pending reports to the FastAPI backend without requiring manual citizen re-entry.

---

## 2. Citizen Reporting & Sync Flow

```
   ┌──────────────────────┐
   │    OPEN APP          │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │    CAMERA SCREEN     │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │  CITIZEN RATING 0–10 │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │     GPS CAPTURE      │
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │  SAVE REPORT LOCALLY │ ──> Copies Image to Persistent Storage
   │ (Status: PENDING_SYNC│     Generates Stable local_incident_id
   └──────────┬───────────┘
              │
              ▼
   ┌──────────────────────┐
   │   CONNECTIVITY CHECK │
   └────┬────────────┬────┘
        │            │
  [ONLINE]        [OFFLINE]
        │            │
        ▼            ▼
┌──────────────┐ ┌────────────────────────────────────────┐
│ UPLOAD NOW   │ │ SHOW OFFLINE SUCCESS                   │
│              │ │ "Report saved on device. It will upload│
│              │ │ when connection returns."              │
└───────┬──────┘ └────────────────────────────────────────┘
        │
   [SUCCESS?]
   ┌────┴────┐
 [YES]      [NO]
   │          │
   ▼          ▼
┌───────────┐┌────────────────────────┐
│ UPLOADED  ││ KEEP AS PENDING_SYNC   │
│ Store     ││ Background Sync Queue  │
│ Server ID ││ Retries with Backoff   │
└───────────┘└────────────────────────┘
```

---

## 3. Local Storage Architecture

### Local Database Schema (`LocalIncident`)
| Field | Type | Description |
| :--- | :--- | :--- |
| `local_id` | `VARCHAR(64)` (PK) | Unique client-generated UUID / timestamp ID |
| `server_id` | `INTEGER` (Nullable) | PostgreSQL ID assigned upon upload confirmation |
| `user_id` | `INTEGER` | Reporting citizen user ID |
| `local_image_path` | `TEXT` | Absolute path to persistent photo in app storage |
| `image_url` | `TEXT` (Nullable) | Remote URL on server post-upload |
| `latitude` | `FLOAT` (Nullable) | GPS latitude (if available) |
| `longitude` | `FLOAT` (Nullable) | GPS longitude (if available) |
| `gps_accuracy` | `FLOAT` (Nullable) | GPS accuracy in metres |
| `location_status` | `VARCHAR(20)` | `AVAILABLE` or `UNAVAILABLE` |
| `timestamp` | `TIMESTAMP` | Original incident capture time |
| `citizen_rating` | `INTEGER` | Citizen severity rating (0–10) |
| `status` | `VARCHAR(20)` | `DRAFT`, `PENDING_SYNC`, `UPLOADING`, `UPLOADED`, `FAILED` |
| `sync_attempts` | `INTEGER` | Cumulative number of upload attempts |
| `last_sync_attempt`| `TIMESTAMP` | Timestamp of most recent upload attempt |
| `last_sync_error` | `TEXT` | Error detail if previous attempt failed |
| `created_at` | `TIMESTAMP` | Local creation timestamp |
| `updated_at` | `TIMESTAMP` | Local modification timestamp |

### Local Image Lifecycle
1. **Capture**: Image initially captured to temporary camera cache.
2. **Preservation**: `LocalImageStorage` immediately copies image into `local_storage/incidents/<local_id>/image.jpg`.
3. **Survivability**: Image persists across app crashes and phone reboots.
4. **Cleanup**: Only after the server responds with a `201 Created` and the local record is updated with `server_id` is temporary cache purged.

---

## 4. Synchronization Queue & Backoff Strategy

### Order of Synchronization
- **FIFO (First-In, First-Out)**: Incidents are processed strictly oldest-first based on `created_at` timestamp.
- **Independent Isolation**: A failure in one incident does not block or cancel subsequent pending incidents.

### Exponential Backoff Policy
- **Base Backoff**: 2 seconds.
- **Formula**: $\text{Delay} = \min(2^{\text{attempts}-1} \times 2, 30)$ seconds.
- **Max Retries**: 4 attempts.
- **Exhaustion**: After 4 failed attempts, status is marked `FAILED` ("Upload needs attention") and preserved indefinitely for manual citizen inspection and one-tap retry.

---

## 5. Backend Idempotency & Duplicate Prevention

To guarantee that network retries never create duplicate incidents in PostgreSQL:
1. Mobile attaches `client_incident_id` in form data and as an `Idempotency-Key` HTTP header.
2. The FastAPI route queries PostgreSQL for an existing record matching `(user_id, client_incident_id)`.
3. If an existing record is found:
   - Returns the existing record (`201 Created`) with `"message": "Incident already exists"`.
   - No new database row is inserted.
   - No redundant image file is written to disk.
4. Mobile receives the existing server ID and updates local status to `UPLOADED`.

---

## 6. Phase 4 Roadmap
In Phase 4, the uploaded and locally synchronized incidents will feed into the **AI Computer Vision Pipeline** (YOLO dataset annotation, model training, and automated civic hazard detection).
