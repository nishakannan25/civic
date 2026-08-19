# Civic AI - Testing Guide

## 1. Backend Test Suite (Pytest)

The backend test suite verifies core security, database ORM models, validation, and REST API contracts using an isolated in-memory SQLite database.

### Running Backend Tests
From the `backend/` directory:
```bash
cd backend
pytest -v
```

### Core Test Cases Executed

| Test ID | Test Name | Target / Verification |
|---|---|---|
| **TEST 1** | `test_health_endpoint_works` | `GET /health` returns status `200` with `status: ok` and service name |
| **TEST 2** | `test_database_connection_works` | Database connection session is created and executes raw scalar query |
| **TEST 3** | `test_user_registration_works` | `POST /auth/register` creates user with bcrypt-hashed password and returns JWT token |
| **TEST 4** | `test_user_login_works` | `POST /auth/login` validates credentials and returns JWT access token |
| **TEST 5** | `test_authenticated_users_me_works` | `GET /users/me` with Bearer token returns current user (excluding password hash) |
| **TEST 6** | `test_unauthenticated_protected_endpoint_rejected` | Accessing `/users/me` without Bearer token is rejected with `401 Unauthorized` |
| **TEST 7** | `test_incident_creation_and_retrieval` (Create) | `POST /incidents` validates payload, creates incident record in `DRAFT` status |
| **TEST 8** | `test_incident_creation_and_retrieval` (Retrieve) | `GET /incidents` and `GET /incidents/{id}` retrieve saved incidents and support updates |

---

## 2. Mobile Client Widget Tests (Flutter)

The Flutter test suite verifies the camera-first UI rendering, theme accessibility, and button interaction handlers.

### Running Mobile Tests
From the `mobile/` directory:
```bash
cd mobile
flutter test
```

---

## 3. Phase 6 Risk Engine Test Suite

The Phase 6 test suite validates pure risk calculation (unit tests), API contracts (HTTP tests), end-to-end incident flow (integration test), and Phase 5 regression tests.

### Running Phase 6 Tests
From the `backend/` directory:

```bash
# Standalone test runner (29 tests)
python run_phase6_tests.py

# Pytest test suite (30 test functions)
python -m pytest tests/test_risk_engine.py -v
```

### Test Case Overview

| Suite | Category | Count | Focus |
|---|---|---|---|
| Section A | Unit Tests | 15 | Pure `RiskEngineService.calculate_score()` logic, boundary values, invalid inputs |
| Section B | API Tests | 10 | `POST /incidents/{id}/risk-assessment` endpoint, HTTP status codes, schema, upserts |
| Section C | Integration | 1 | E2E incident creation → Phase 5 AI setting → Phase 6 risk calculation |
| Section D | Regression | 2 | Phase 5 `/ai/health` and `/ai/infer` remain functional |

