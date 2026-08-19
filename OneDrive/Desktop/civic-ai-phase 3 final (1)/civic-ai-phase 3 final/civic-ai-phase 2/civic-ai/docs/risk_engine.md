# Phase 6 — Risk Engine

## Overview

The Risk Engine is a deterministic, configurable module that transforms Phase 5 AI inference results combined with citizen input and location data into a structured risk assessment for each civic incident.

**Purpose**: Determine how urgent an incident is so that field teams can prioritise response.

**Non-goal**: The Risk Engine does NOT route incidents to departments, send notifications, or implement community voting. Those belong to later phases.

---

## Architecture

```
Citizen Report
      │
      ▼
Phase 5 AI Inference
  (MobileNetV3, 6 classes)
      │
      ▼ crisis_class + ai_confidence
      │
Phase 6 Risk Engine
  (RiskEngineService)
      │
      ├── crisis_severity_weight   (from RISK_CONFIG)
      ├── ai_confidence            (0.0–1.0)
      ├── citizen_rating           (0–10 → 0.0–1.0)
      └── location_available       (bool → 0.0 or 1.0)
      │
      ▼
  risk_score (0–100)
      │
      ├── risk_level   (LOW / MEDIUM / HIGH / CRITICAL)
      ├── priority     (LOW / NORMAL / HIGH / URGENT)
      └── explanation  (deterministic text)
      │
      ▼
  RiskAssessment DB Record
```

**Layer separation** (strictly enforced):

```
API Route (incidents.py)
    ↓ delegates to
RiskEngineService (risk_service.py)
    ↓ reads config from
Settings.RISK_CONFIG (config.py)
    ↓ persists to
risk_assessments table (PostgreSQL / SQLite)
```

No scoring logic lives in the API route, database model, mobile widgets, or AI inference service.

---

## Inputs

| Field | Source | Type | Range |
|---|---|---|---|
| `incident_id` | Incident table | int | — |
| `ai_issue_type` | Phase 5 AI result | int (0–5) | `AITaxonomyClass` enum |
| `ai_confidence` | Phase 5 AI result | float | 0.0–1.0 |
| `citizen_rating` | Phase 2 form | int | 0–10 |
| `location_status` | Phase 2 GPS | string | AVAILABLE / UNAVAILABLE |
| `latitude`, `longitude` | Phase 2 GPS | float/null | WGS-84 |

---

## Scoring Formula

```
normalized_severity  = crisis_severity / 100.0
normalized_confidence = ai_confidence
normalized_rating    = citizen_rating / 10.0
location_component   = 1.0 if AVAILABLE else 0.0

raw_score = (
      normalized_severity   × SEVERITY_WEIGHT
    + normalized_confidence × CONFIDENCE_WEIGHT
    + normalized_rating     × CITIZEN_RATING_WEIGHT
    + location_component    × LOCATION_WEIGHT
)

risk_score = clamp(raw_score × 100, 0.0, 100.0)   [rounded to 2 dp]
```

### Example — Open Manhole, high inputs

```
crisis_severity  = 95  → normalized = 0.95
ai_confidence    = 0.94
citizen_rating   = 9   → normalized = 0.90
location         = available → 1.0

raw_score = 0.95×0.40 + 0.94×0.30 + 0.90×0.20 + 1.0×0.10
          = 0.380 + 0.282 + 0.180 + 0.100
          = 0.942

risk_score = 94.2 / 100  →  CRITICAL  →  URGENT
```

---

## Crisis Severity Configuration

All values are in the `RISK_CONFIG.crisis_severity` section. **These are prototype defaults, not official emergency classifications.**

| Crisis Class | Default Severity | Rationale |
|---|---|---|
| `open_manhole` | 95 | Immediate physical danger |
| `flooding` | 90 | Large-scale hazard |
| `pothole` | 70 | Road safety, vehicle damage |
| `water_leakage` | 60 | Infrastructure degradation |
| `broken_streetlight` | 50 | Safety at night |
| `garbage` | 40 | Environmental, health concern |

Modify these defaults by setting `RISK_CONFIG` in `.env`:
```env
RISK_CONFIG={"crisis_severity": {"open_manhole": 95, ...}, ...}
```

---

## Scoring Weights

| Component | Default Weight | Description |
|---|---|---|
| `severity` | 0.40 | Crisis type baseline (largest contributor) |
| `confidence` | 0.30 | AI classification certainty |
| `citizen_rating` | 0.20 | Self-reported severity by citizen |
| `location` | 0.10 | GPS availability bonus |

**Sum of weights = 1.00** (guaranteed at default values).

---

## Risk Level Thresholds

| Score Range | Risk Level | Priority | Meaning |
|---|---|---|---|
| 0–24 | LOW | LOW | Monitor; non-urgent |
| 25–49 | MEDIUM | NORMAL | Requires attention |
| 50–74 | HIGH | HIGH | Prompt action needed |
| 75–100 | CRITICAL | URGENT | Immediate response |

Thresholds are configurable via `RISK_CONFIG.thresholds`.

---

## Risk Explanation

Explanations are generated deterministically from the actual input values. No LLM is used.

**Example output:**

```
This is a CRITICAL incident requiring immediate response.
The detected category (Open Manhole) has a very high baseline severity (95/100).
AI confidence is strong (94%).
Citizen-reported severity is high (9/10).
GPS location is available, aiding field response.
Calculated risk score: 94.2/100.
```

Explanation qualifiers:

| Value | Label used |
|---|---|
| crisis_severity ≥ 85 | "very high" |
| crisis_severity ≥ 65 | "high" |
| crisis_severity ≥ 45 | "medium" |
| else | "lower" |
| confidence ≥ 0.80 | "strong" |
| confidence ≥ 0.50 | "moderate" |
| else | "weak" |
| citizen_rating ≥ 8 | "high" |
| citizen_rating ≥ 5 | "moderate" |
| else | "low" |

---

## Priority Mapping

```
LOW      → LOW
MEDIUM   → NORMAL
HIGH     → HIGH
CRITICAL → URGENT
```

Configurable via `RISK_CONFIG.priority_map`.

---

## API Contract

```
POST /api/v1/incidents/{incident_id}/risk-assessment
Authorization: Bearer <token>

Response 200:
{
  "incident_id": 42,
  "risk_score": 94.2,
  "risk_level": "CRITICAL",
  "priority": "URGENT",
  "crisis_class": "open_manhole",
  "crisis_severity": 95.0,
  "ai_confidence": 0.94,
  "citizen_rating": 9,
  "location_available": true,
  "explanation": "This is a CRITICAL incident ...",
  "calculated_at": "2026-08-17T15:40:00Z"
}
```

Error responses:
- `404` — incident not found
- `422` — missing AI result, invalid confidence, invalid rating, unknown crisis class
- `401/403` — authentication required

---

## Database Model

Table: `risk_assessments`

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER PK | Auto-increment |
| `incident_id` | INTEGER FK | → incidents.id, UNIQUE |
| `risk_score` | FLOAT | 0.0–100.0 |
| `risk_level` | VARCHAR(20) | LOW / MEDIUM / HIGH / CRITICAL |
| `priority` | VARCHAR(20) | LOW / NORMAL / HIGH / URGENT |
| `crisis_class` | VARCHAR(50) | Raw class key |
| `crisis_severity` | FLOAT | Baseline severity used |
| `ai_confidence` | FLOAT | Confidence used |
| `citizen_rating` | INTEGER | Rating used |
| `location_available` | BOOLEAN | GPS availability flag |
| `explanation` | TEXT | Human-readable explanation |
| `calculated_at` | DATETIME | UTC calculation time |

**One-to-one with incidents** (enforced by `UniqueConstraint`). Repeated calls upsert — no duplicates.

---

## Phase 6 Limitations

- Risk Engine does NOT route incidents to departments (Phase 7+).
- Risk Engine does NOT use community voting or verification results.
- Risk Engine does NOT make emergency service calls.
- Risk engine does NOT use reinforcement learning.
- Explanation is deterministic rule-based text — not AI-generated prose.
- Crisis severity weights are prototype defaults — not official emergency classification standards.
