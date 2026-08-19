#!/usr/bin/env python3
"""
Civic AI — Phase 6 Risk Engine Verification & Integration Test Runner

Tests:
  Section A: Unit tests   — Pure RiskEngineService.calculate_score() (no DB, no HTTP)
  Section B: API tests    — Full HTTP via FastAPI TestClient + SQLite in-memory
  Section C: Integration  — End-to-end incident → risk assessment flow
  Section D: Regression   — Phase 5 /ai/health and /ai/infer still work

Total: 29 tests
"""

import io
import os
import sys
from datetime import datetime, timezone
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_DIR, ".."))
sys.path.insert(0, BACKEND_DIR)
sys.path.insert(0, PROJECT_ROOT)

from app.main import app
from app.database.base import Base
from app.database.connection import get_db
from app.core.constants import AITaxonomyClass, AI_TAXONOMY_MAP
from app.services.risk_service import RiskEngineService
from app.ai.model_loader import ModelLoader

# ─────────────────────────────────────────────────────────────────────────────
# In-memory SQLite test database
# ─────────────────────────────────────────────────────────────────────────────
test_engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def create_test_image(color=(100, 150, 200), size=(224, 224), fmt="JPEG") -> bytes:
    """Create a synthetic solid-color image for upload tests."""
    buf = io.BytesIO()
    Image.new("RGB", size, color).save(buf, format=fmt)
    return buf.getvalue()


def run_tests():
    print("=" * 75)
    print("  CIVIC AI - PHASE 6 RISK ENGINE TEST SUITE")
    print("=" * 75)

    passed = 0
    failed = 0
    total_tests = 28

    # ── DB + Client Setup ─────────────────────────────────────────────────────
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    # Helper: register a user and get token
    def _register_and_login(email="risktest@civic.ai", password="SecurePass123!"):
        resp = client.post("/auth/register", json={
            "email": email,
            "password": password,
            "name": "Risk Test User",
        })
        if resp.status_code == 201:
            return resp.json().get("access_token", "")
        resp_login = client.post("/auth/login", json={"email": email, "password": password})
        return resp_login.json().get("access_token", "")

    token = _register_and_login()
    auth_headers = {"Authorization": f"Bearer {token}"}

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION A — UNIT TESTS (Pure RiskEngineService.calculate_score)
    # ─────────────────────────────────────────────────────────────────────────
    print("\n-- SECTION A: Unit Tests (Pure scoring, no DB) --")

    # TEST A1: Open manhole — high confidence, high rating, location available
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="open_manhole",
            ai_confidence=0.94,
            citizen_rating=9,
            location_available=True,
        )
        score = result["risk_score"]
        assert result["risk_level"] in ("HIGH", "CRITICAL"), f"Expected HIGH or CRITICAL, got {result['risk_level']}"
        assert result["priority"] in ("HIGH", "URGENT"), f"Expected HIGH or URGENT, got {result['priority']}"
        assert 0 <= score <= 100
        print(f"[PASS] A1: Open manhole high conf/rating → score={score:.1f} level={result['risk_level']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A1: {e}"); failed += 1

    # TEST A2: Flooding — high confidence, high rating
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="flooding",
            ai_confidence=0.96,
            citizen_rating=10,
            location_available=True,
        )
        assert result["risk_level"] in ("HIGH", "CRITICAL")
        print(f"[PASS] A2: Flooding high conf/rating → score={result['risk_score']:.1f} level={result['risk_level']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A2: {e}"); failed += 1

    # TEST A3: Garbage — low citizen rating
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="garbage",
            ai_confidence=0.90,
            citizen_rating=3,
            location_available=True,
        )
        assert result["risk_level"] in ("LOW", "MEDIUM"), f"Expected LOW/MEDIUM, got {result['risk_level']}"
        print(f"[PASS] A3: Garbage low rating → score={result['risk_score']:.1f} level={result['risk_level']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A3: {e}"); failed += 1

    # TEST A4: Broken streetlight — medium confidence
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="broken_streetlight",
            ai_confidence=0.60,
            citizen_rating=5,
            location_available=True,
        )
        assert 0 <= result["risk_score"] <= 100
        assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        print(f"[PASS] A4: Broken streetlight medium conf → score={result['risk_score']:.1f} level={result['risk_level']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A4: {e}"); failed += 1

    # TEST A5: Water leakage — location available
    try:
        result_with_loc = RiskEngineService.calculate_score(
            crisis_class="water_leakage",
            ai_confidence=0.75,
            citizen_rating=6,
            location_available=True,
        )
        result_no_loc = RiskEngineService.calculate_score(
            crisis_class="water_leakage",
            ai_confidence=0.75,
            citizen_rating=6,
            location_available=False,
        )
        assert result_with_loc["risk_score"] > result_no_loc["risk_score"], \
            "Location available should produce higher score"
        print(f"[PASS] A5: Water leakage with/without location → {result_with_loc['risk_score']:.1f} vs {result_no_loc['risk_score']:.1f}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A5: {e}"); failed += 1

    # TEST A6: Pothole — location unavailable
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="pothole",
            ai_confidence=0.85,
            citizen_rating=7,
            location_available=False,
        )
        assert result["location_component"] == 0.0, "location_component must be 0.0 when unavailable"
        print(f"[PASS] A6: Pothole location unavailable → location_component=0.0 score={result['risk_score']:.1f}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A6: {e}"); failed += 1

    # TEST A7: AI confidence = 0
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="flooding",
            ai_confidence=0.0,
            citizen_rating=5,
            location_available=True,
        )
        assert 0 <= result["risk_score"] <= 100
        assert result["normalized_confidence"] == 0.0
        print(f"[PASS] A7: AI confidence=0.0 → score={result['risk_score']:.1f} (not forced critical)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A7: {e}"); failed += 1

    # TEST A8: AI confidence = 1
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="flooding",
            ai_confidence=1.0,
            citizen_rating=5,
            location_available=True,
        )
        assert 0 <= result["risk_score"] <= 100
        assert result["normalized_confidence"] == 1.0
        print(f"[PASS] A8: AI confidence=1.0 → score={result['risk_score']:.1f}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A8: {e}"); failed += 1

    # TEST A9: Citizen rating = 0
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="open_manhole",
            ai_confidence=0.90,
            citizen_rating=0,
            location_available=True,
        )
        assert result["normalized_rating"] == 0.0, f"Normalized rating should be 0.0, got {result['normalized_rating']}"
        print(f"[PASS] A9: Citizen rating=0 → normalized_rating=0.0 score={result['risk_score']:.1f}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A9: {e}"); failed += 1

    # TEST A10: Citizen rating = 10
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="open_manhole",
            ai_confidence=0.90,
            citizen_rating=10,
            location_available=True,
        )
        assert result["normalized_rating"] == 1.0, f"Normalized rating should be 1.0, got {result['normalized_rating']}"
        print(f"[PASS] A10: Citizen rating=10 → normalized_rating=1.0 score={result['risk_score']:.1f}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A10: {e}"); failed += 1

    # TEST A11: Risk score never exceeds 100
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="open_manhole",
            ai_confidence=1.0,
            citizen_rating=10,
            location_available=True,
        )
        assert result["risk_score"] <= 100.0, f"Score exceeded 100: {result['risk_score']}"
        print(f"[PASS] A11: Score never exceeds 100 → {result['risk_score']:.2f}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A11: {e}"); failed += 1

    # TEST A12: Risk score never falls below 0
    try:
        result = RiskEngineService.calculate_score(
            crisis_class="garbage",
            ai_confidence=0.0,
            citizen_rating=0,
            location_available=False,
        )
        assert result["risk_score"] >= 0.0, f"Score below 0: {result['risk_score']}"
        print(f"[PASS] A12: Score never below 0 → {result['risk_score']:.2f}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A12: {e}"); failed += 1

    # TEST A13: Same inputs → same risk result (determinism)
    try:
        r1 = RiskEngineService.calculate_score("pothole", 0.91, 8, True)
        r2 = RiskEngineService.calculate_score("pothole", 0.91, 8, True)
        assert r1["risk_score"] == r2["risk_score"], f"Non-deterministic: {r1['risk_score']} vs {r2['risk_score']}"
        assert r1["risk_level"] == r2["risk_level"]
        assert r1["priority"]   == r2["priority"]
        assert r1["explanation"] == r2["explanation"]
        print(f"[PASS] A13: Deterministic — same inputs → same result ({r1['risk_score']:.2f})")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A13: {e}"); failed += 1

    # TEST A14: Invalid crisis class is rejected
    try:
        raised = False
        try:
            RiskEngineService.calculate_score("alien_invasion", 0.90, 5, True)
        except ValueError as ve:
            raised = True
            assert "alien_invasion" in str(ve).lower() or "unknown" in str(ve).lower()
        assert raised, "ValueError not raised for unknown crisis class"
        print("[PASS] A14: Unknown crisis class raises ValueError")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A14: {e}"); failed += 1

    # TEST A15: Invalid confidence rejected
    try:
        raised = False
        try:
            RiskEngineService.calculate_score("pothole", 1.5, 5, True)
        except ValueError:
            raised = True
        assert raised, "ValueError not raised for confidence > 1.0"
        print("[PASS] A15: Invalid confidence (1.5) raises ValueError")
        passed += 1
    except Exception as e:
        print(f"[FAIL] A15: {e}"); failed += 1

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION B — API TESTS
    # ─────────────────────────────────────────────────────────────────────────
    print("\n-- SECTION B: API Tests (HTTP via TestClient) --")

    # Helper: create an incident and seed AI result fields directly on ORM
    def _create_incident_with_ai(
        ai_issue_type=1,  # open_manhole
        ai_confidence=0.94,
        citizen_rating=9,
        location_status="AVAILABLE",
        latitude=12.9716,
        longitude=77.5946,
    ):
        """Create incident via API, then manually set AI fields on DB object."""
        img = create_test_image()
        resp = client.post(
            "/incidents",
            files={"image": ("test.jpg", io.BytesIO(img), "image/jpeg")},
            data={
                "citizen_rating": str(citizen_rating),
                "location_status": location_status,
                "latitude": str(latitude) if latitude else "",
                "longitude": str(longitude) if longitude else "",
            },
            headers=auth_headers,
        )
        assert resp.status_code == 201, f"Incident creation failed: {resp.status_code} {resp.text}"
        incident_id = resp.json()["id"]

        # Manually set AI fields (simulating Phase 5 inference result persisted on incident)
        from app.models.incident import Incident as IncidentModel
        incident_obj = session.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
        incident_obj.ai_issue_type = ai_issue_type
        incident_obj.ai_confidence = ai_confidence
        session.commit()
        session.refresh(incident_obj)

        return incident_id

    # TEST B1: Valid risk assessment request
    try:
        inc_id = _create_incident_with_ai(ai_issue_type=1, ai_confidence=0.94, citizen_rating=9)
        resp = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        body = resp.json()
        assert body["incident_id"] == inc_id
        assert "risk_score" in body
        assert "risk_level" in body
        assert "priority" in body
        assert "explanation" in body
        assert "calculated_at" in body
        assert 0 <= body["risk_score"] <= 100
        assert body["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        print(f"[PASS] B1: Valid assessment → score={body['risk_score']:.1f} level={body['risk_level']}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B1: {e}"); failed += 1

    # TEST B2: Missing incident (404)
    try:
        resp = client.post("/incidents/999999/risk-assessment", headers=auth_headers)
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}"
        print("[PASS] B2: Missing incident → 404 Not Found")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B2: {e}"); failed += 1

    # TEST B3: Incident without AI result → 422
    try:
        img = create_test_image()
        resp_create = client.post(
            "/incidents",
            files={"image": ("noai.jpg", io.BytesIO(img), "image/jpeg")},
            data={"citizen_rating": "7", "location_status": "UNAVAILABLE"},
            headers=auth_headers,
        )
        no_ai_id = resp_create.json()["id"]
        resp = client.post(f"/incidents/{no_ai_id}/risk-assessment", headers=auth_headers)
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}"
        assert "ai inference" in resp.json()["detail"].lower() or "ai_issue_type" in resp.json()["detail"].lower()
        print("[PASS] B3: Incident without AI result → 422 with clear message")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B3: {e}"); failed += 1

    # TEST B4: Risk assessment response schema validation
    try:
        inc_id = _create_incident_with_ai(ai_issue_type=0, ai_confidence=0.85, citizen_rating=7)
        resp = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        body = resp.json()
        required_fields = [
            "incident_id", "risk_score", "risk_level", "priority",
            "crisis_class", "crisis_severity", "ai_confidence",
            "citizen_rating", "location_available", "explanation", "calculated_at",
        ]
        for field in required_fields:
            assert field in body, f"Missing field: {field}"
        print(f"[PASS] B4: Response schema contains all {len(required_fields)} required fields")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B4: {e}"); failed += 1

    # TEST B5: Repeated assessment does NOT create duplicate DB records
    try:
        from app.models.risk_assessment import RiskAssessment
        inc_id = _create_incident_with_ai(ai_issue_type=2, ai_confidence=0.80, citizen_rating=5)
        client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        count = session.query(RiskAssessment).filter(RiskAssessment.incident_id == inc_id).count()
        assert count == 1, f"Expected 1 assessment record, found {count}"
        print("[PASS] B5: Repeated assessment calls produce exactly 1 DB record (upsert)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B5: {e}"); failed += 1

    # TEST B6: Same inputs produce same result on repeated call (determinism via API)
    try:
        inc_id = _create_incident_with_ai(ai_issue_type=3, ai_confidence=0.75, citizen_rating=6)
        r1 = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers).json()
        r2 = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers).json()
        assert r1["risk_score"]  == r2["risk_score"],  "risk_score changed on repeat call"
        assert r1["risk_level"]  == r2["risk_level"],  "risk_level changed on repeat call"
        assert r1["priority"]    == r2["priority"],    "priority changed on repeat call"
        assert r1["explanation"] == r2["explanation"], "explanation changed on repeat call"
        print(f"[PASS] B6: Repeated API call produces identical result (deterministic)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B6: {e}"); failed += 1

    # TEST B7: Unauthenticated request → 401/403
    try:
        inc_id = _create_incident_with_ai()
        resp = client.post(f"/incidents/{inc_id}/risk-assessment")  # No auth header
        assert resp.status_code in (401, 403), f"Expected 401/403, got {resp.status_code}"
        print("[PASS] B7: Unauthenticated request → 401/403")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B7: {e}"); failed += 1

    # TEST B8: risk_score is within [0, 100]
    try:
        inc_id = _create_incident_with_ai(ai_issue_type=1, ai_confidence=1.0, citizen_rating=10)
        resp = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        score = resp.json()["risk_score"]
        assert 0 <= score <= 100, f"Score out of range: {score}"
        print(f"[PASS] B8: Risk score within [0, 100] → {score}")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B8: {e}"); failed += 1

    # TEST B9: risk_level maps to valid priority
    try:
        level_to_priority = {"LOW": "LOW", "MEDIUM": "NORMAL", "HIGH": "HIGH", "CRITICAL": "URGENT"}
        inc_id = _create_incident_with_ai(ai_issue_type=4, ai_confidence=0.70, citizen_rating=5)
        body = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers).json()
        expected_priority = level_to_priority.get(body["risk_level"])
        assert body["priority"] == expected_priority, \
            f"Level {body['risk_level']} should map to {expected_priority}, got {body['priority']}"
        print(f"[PASS] B9: risk_level={body['risk_level']} → priority={body['priority']} (correct mapping)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B9: {e}"); failed += 1

    # TEST B10: Incident status updated to RISK_ASSESSED after assessment
    try:
        from app.models.incident import Incident as IncidentModel
        inc_id = _create_incident_with_ai(ai_issue_type=5, ai_confidence=0.77, citizen_rating=6)
        client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        session.expire_all()
        incident_obj = session.query(IncidentModel).filter(IncidentModel.id == inc_id).first()
        assert incident_obj.status == "RISK_ASSESSED", f"Expected RISK_ASSESSED, got {incident_obj.status}"
        print(f"[PASS] B10: Incident status updated to RISK_ASSESSED after assessment")
        passed += 1
    except Exception as e:
        print(f"[FAIL] B10: {e}"); failed += 1

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION C — INTEGRATION TEST
    # ─────────────────────────────────────────────────────────────────────────
    print("\n-- SECTION C: Integration Test (full flow) --")

    # TEST C1: Create incident → set AI → risk assess → verify full result
    try:
        img = create_test_image(color=(200, 100, 80))
        resp_create = client.post(
            "/incidents",
            files={"image": ("pothole_test.jpg", io.BytesIO(img), "image/jpeg")},
            data={
                "citizen_rating": "8",
                "location_status": "AVAILABLE",
                "latitude": "12.9716",
                "longitude": "77.5946",
            },
            headers=auth_headers,
        )
        assert resp_create.status_code == 201
        inc_id = resp_create.json()["id"]

        # Simulate Phase 5: set pothole AI result
        from app.models.incident import Incident as IncidentModel
        incident_obj = session.query(IncidentModel).filter(IncidentModel.id == inc_id).first()
        incident_obj.ai_issue_type = AITaxonomyClass.POTHOLE  # 0 = pothole
        incident_obj.ai_confidence = 0.91
        session.commit()

        # Call Phase 6 Risk Engine
        resp_risk = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        assert resp_risk.status_code == 200
        body = resp_risk.json()

        assert body["crisis_class"] == "pothole"
        assert body["crisis_severity"] == 70.0
        assert body["ai_confidence"] == 0.91
        assert body["citizen_rating"] == 8
        assert body["location_available"] is True
        assert 0 <= body["risk_score"] <= 100
        assert body["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")
        assert body["priority"] in ("LOW", "NORMAL", "HIGH", "URGENT")
        assert len(body["explanation"]) > 20

        print(
            f"[PASS] C1: Full integration flow → pothole incident "
            f"score={body['risk_score']:.1f} level={body['risk_level']} "
            f"priority={body['priority']}"
        )
        passed += 1
    except Exception as e:
        print(f"[FAIL] C1: {e}"); failed += 1

    # ─────────────────────────────────────────────────────────────────────────
    # SECTION D — PHASE 5 REGRESSION TESTS
    # ─────────────────────────────────────────────────────────────────────────
    print("\n-- SECTION D: Phase 5 Regression --")

    # TEST D1: GET /ai/health still returns ready
    try:
        ModelLoader.load()
        resp = client.get("/ai/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["status"] == "ready"
        assert body["model_loaded"] is True
        print("[PASS] D1: Phase 5 GET /ai/health still returns ready (regression)")
        passed += 1
    except Exception as e:
        print(f"[FAIL] D1: {e}"); failed += 1

    # TEST D2: POST /ai/infer still works with a valid image
    try:
        img = create_test_image()
        files = {"image": ("check.jpg", io.BytesIO(img), "image/jpeg")}
        resp = client.post("/ai/infer", files=files)
        assert resp.status_code == 200
        body = resp.json()
        assert "predicted_class" in body
        assert "confidence" in body
        assert 0.0 <= body["confidence"] <= 1.0
        print(f"[PASS] D2: Phase 5 POST /ai/infer still works (predicted={body['predicted_class']}, conf={body['confidence']:.3f})")
        passed += 1
    except Exception as e:
        print(f"[FAIL] D2: {e}"); failed += 1

    # ─────────────────────────────────────────────────────────────────────────
    # RESULTS
    # ─────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 75)
    print(f"  RESULTS: {passed}/{total_tests} Tests Passed | {failed} Failed")
    print("=" * 75)

    if passed == total_tests:
        print("  ✅  All Phase 6 tests passed. Risk Engine is working correctly.")
    else:
        print(f"  ❌  {failed} test(s) failed. Review the output above.")

    # Cleanup
    Base.metadata.drop_all(bind=test_engine)
    session.close()
    app.dependency_overrides.clear()

    return passed == total_tests


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
