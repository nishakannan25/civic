"""Phase 6 — pytest test suite for the Risk Engine.

Covers:
  - Unit tests: pure RiskEngineService.calculate_score()
  - API tests: POST /incidents/{id}/risk-assessment via TestClient
  - Determinism verification
  - Invalid input handling

Run with:
    pytest tests/test_risk_engine.py -v
"""

import io
import pytest
from PIL import Image
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.constants import AITaxonomyClass
from app.models.incident import Incident
from app.models.risk_assessment import RiskAssessment
from app.services.risk_service import RiskEngineService


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

def _make_image_bytes(color=(100, 150, 200)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (224, 224), color).save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture(scope="function")
def auth_token(client: TestClient) -> str:
    """Register a test user and return a JWT access token."""
    resp = client.post("/auth/register", json={
        "email": "pytest_risk@civic.ai",
        "password": "Test1234!",
        "name": "Pytest Risk User",
    })
    if resp.status_code == 201:
        return resp.json().get("access_token", "")
    resp_login = client.post("/auth/login", json={
        "email": "pytest_risk@civic.ai",
        "password": "Test1234!",
    })
    return resp_login.json().get("access_token", "")


@pytest.fixture(scope="function")
def auth_headers(auth_token: str) -> dict:
    return {"Authorization": f"Bearer {auth_token}"}


def _create_incident_with_ai(
    client: TestClient,
    db_session: Session,
    auth_headers: dict,
    ai_issue_type: int = 1,
    ai_confidence: float = 0.90,
    citizen_rating: int = 8,
    location_status: str = "AVAILABLE",
    latitude: float = 12.9716,
    longitude: float = 77.5946,
) -> int:
    """Create an incident and patch AI fields directly on the ORM object."""
    img = _make_image_bytes()
    data = {
        "citizen_rating": str(citizen_rating),
        "location_status": location_status,
        "latitude": str(latitude) if location_status == "AVAILABLE" else "",
        "longitude": str(longitude) if location_status == "AVAILABLE" else "",
    }
    resp = client.post(
        "/incidents",
        files={"image": ("test.jpg", io.BytesIO(img), "image/jpeg")},
        data=data,
        headers=auth_headers,
    )
    assert resp.status_code == 201, f"Failed to create incident: {resp.text}"
    incident_id = resp.json()["id"]

    # Patch AI fields (simulates Phase 5 result being persisted)
    inc = db_session.query(Incident).filter(Incident.id == incident_id).first()
    inc.ai_issue_type = ai_issue_type
    inc.ai_confidence = ai_confidence
    db_session.commit()
    db_session.refresh(inc)
    return incident_id


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TESTS — Pure scoring (no DB, no HTTP)
# ─────────────────────────────────────────────────────────────────────────────

class TestRiskScoreCalculation:

    def test_open_manhole_high_confidence_high_rating_is_high_or_critical(self):
        """TEST A1: Open manhole + high conf + high rating → HIGH or CRITICAL."""
        result = RiskEngineService.calculate_score("open_manhole", 0.94, 9, True)
        assert result["risk_level"] in ("HIGH", "CRITICAL")
        assert result["priority"] in ("HIGH", "URGENT")

    def test_flooding_critical_scenario(self):
        """TEST A2: Flooding + max conf + max rating → HIGH or CRITICAL."""
        result = RiskEngineService.calculate_score("flooding", 0.96, 10, True)
        assert result["risk_level"] in ("HIGH", "CRITICAL")

    def test_garbage_low_rating_is_low_or_medium(self):
        """TEST A3: Garbage + low citizen rating → LOW or MEDIUM."""
        result = RiskEngineService.calculate_score("garbage", 0.90, 3, True)
        assert result["risk_level"] in ("LOW", "MEDIUM")

    def test_broken_streetlight_medium_confidence(self):
        """TEST A4: Broken streetlight + medium conf → valid score."""
        result = RiskEngineService.calculate_score("broken_streetlight", 0.60, 5, True)
        assert 0 <= result["risk_score"] <= 100
        assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_location_available_produces_higher_score(self):
        """TEST A5: Location available adds to score vs unavailable."""
        r_with = RiskEngineService.calculate_score("water_leakage", 0.75, 6, True)
        r_without = RiskEngineService.calculate_score("water_leakage", 0.75, 6, False)
        assert r_with["risk_score"] > r_without["risk_score"]

    def test_location_unavailable_zeroes_component(self):
        """TEST A6: location_component = 0.0 when location unavailable."""
        result = RiskEngineService.calculate_score("pothole", 0.85, 7, False)
        assert result["location_component"] == 0.0

    def test_zero_confidence_does_not_force_critical(self):
        """TEST A7: AI confidence=0 should reduce, not inflate, risk."""
        result_zero = RiskEngineService.calculate_score("flooding", 0.0, 5, True)
        result_high = RiskEngineService.calculate_score("flooding", 0.90, 5, True)
        assert result_zero["risk_score"] < result_high["risk_score"]
        assert result_zero["normalized_confidence"] == 0.0

    def test_full_confidence(self):
        """TEST A8: AI confidence=1.0 maximizes confidence component."""
        result = RiskEngineService.calculate_score("flooding", 1.0, 5, True)
        assert result["normalized_confidence"] == 1.0
        assert 0 <= result["risk_score"] <= 100

    def test_zero_citizen_rating(self):
        """TEST A9: citizen_rating=0 → normalized_rating=0.0."""
        result = RiskEngineService.calculate_score("open_manhole", 0.90, 0, True)
        assert result["normalized_rating"] == 0.0

    def test_max_citizen_rating(self):
        """TEST A10: citizen_rating=10 → normalized_rating=1.0."""
        result = RiskEngineService.calculate_score("open_manhole", 0.90, 10, True)
        assert result["normalized_rating"] == 1.0

    def test_risk_score_never_exceeds_100(self):
        """TEST A11: Maximum possible inputs still yield score ≤ 100."""
        result = RiskEngineService.calculate_score("open_manhole", 1.0, 10, True)
        assert result["risk_score"] <= 100.0

    def test_risk_score_never_below_0(self):
        """TEST A12: Minimum inputs still yield score ≥ 0."""
        result = RiskEngineService.calculate_score("garbage", 0.0, 0, False)
        assert result["risk_score"] >= 0.0

    def test_same_inputs_produce_same_result(self):
        """TEST A13: Determinism — identical inputs → identical outputs."""
        r1 = RiskEngineService.calculate_score("pothole", 0.91, 8, True)
        r2 = RiskEngineService.calculate_score("pothole", 0.91, 8, True)
        assert r1["risk_score"]   == r2["risk_score"]
        assert r1["risk_level"]   == r2["risk_level"]
        assert r1["priority"]     == r2["priority"]
        assert r1["explanation"]  == r2["explanation"]

    def test_invalid_crisis_class_raises_value_error(self):
        """TEST A14: Unknown crisis class must raise ValueError."""
        with pytest.raises(ValueError, match="Unknown crisis class"):
            RiskEngineService.calculate_score("flying_saucer", 0.90, 5, True)

    def test_confidence_out_of_range_raises_value_error(self):
        """TEST A15: Confidence outside [0, 1] must raise ValueError."""
        with pytest.raises(ValueError, match="ai_confidence"):
            RiskEngineService.calculate_score("pothole", 1.5, 5, True)

    def test_invalid_citizen_rating_raises_value_error(self):
        """TEST A16: citizen_rating outside [0, 10] must raise ValueError."""
        with pytest.raises(ValueError, match="citizen_rating"):
            RiskEngineService.calculate_score("pothole", 0.80, 11, True)

    def test_negative_confidence_raises_value_error(self):
        """TEST A17: Negative confidence must raise ValueError."""
        with pytest.raises(ValueError):
            RiskEngineService.calculate_score("pothole", -0.1, 5, True)

    def test_explanation_is_non_empty_string(self):
        """TEST A18: Explanation must be a non-empty string."""
        result = RiskEngineService.calculate_score("flooding", 0.80, 7, True)
        assert isinstance(result["explanation"], str)
        assert len(result["explanation"]) > 30

    def test_all_six_crisis_classes_are_supported(self):
        """TEST A19: All 6 crisis classes produce valid results."""
        classes = ["pothole", "open_manhole", "garbage", "flooding", "broken_streetlight", "water_leakage"]
        for cls in classes:
            result = RiskEngineService.calculate_score(cls, 0.75, 5, True)
            assert 0 <= result["risk_score"] <= 100, f"Invalid score for {cls}"
            assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH", "CRITICAL")

    def test_risk_level_thresholds_mapping(self):
        """TEST A20: Risk levels map to correct priorities."""
        level_map = {
            "LOW": "LOW",
            "MEDIUM": "NORMAL",
            "HIGH": "HIGH",
            "CRITICAL": "URGENT",
        }
        for level, expected_priority in level_map.items():
            priority = RiskEngineService.determine_priority(level)
            assert priority == expected_priority, f"{level} should map to {expected_priority}, got {priority}"


# ─────────────────────────────────────────────────────────────────────────────
# API TESTS — HTTP endpoints
# ─────────────────────────────────────────────────────────────────────────────

class TestRiskAssessmentAPI:

    def test_valid_request_returns_200(self, client, db_session, auth_headers):
        """TEST B1: Valid request returns 200 with correct schema."""
        inc_id = _create_incident_with_ai(client, db_session, auth_headers)
        resp = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["incident_id"] == inc_id
        assert "risk_score" in body
        assert "risk_level" in body
        assert "priority" in body
        assert "explanation" in body

    def test_missing_incident_returns_404(self, client, auth_headers):
        """TEST B2: Non-existent incident → 404."""
        resp = client.post("/incidents/999999/risk-assessment", headers=auth_headers)
        assert resp.status_code == 404

    def test_incident_without_ai_result_returns_422(self, client, db_session, auth_headers):
        """TEST B3: Incident with no AI result → 422 with clear error."""
        img = _make_image_bytes()
        resp_create = client.post(
            "/incidents",
            files={"image": ("noai.jpg", io.BytesIO(img), "image/jpeg")},
            data={"citizen_rating": "5", "location_status": "UNAVAILABLE"},
            headers=auth_headers,
        )
        inc_id = resp_create.json()["id"]
        resp = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        assert resp.status_code == 422

    def test_response_contains_all_required_fields(self, client, db_session, auth_headers):
        """TEST B4: Response schema contains all 11 required fields."""
        inc_id = _create_incident_with_ai(client, db_session, auth_headers, ai_issue_type=0)
        body = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers).json()
        for field in ["incident_id", "risk_score", "risk_level", "priority",
                      "crisis_class", "crisis_severity", "ai_confidence",
                      "citizen_rating", "location_available", "explanation", "calculated_at"]:
            assert field in body, f"Missing field in response: {field}"

    def test_repeated_call_does_not_duplicate_db_record(self, client, db_session, auth_headers):
        """TEST B5: Calling the endpoint twice produces exactly 1 DB record."""
        inc_id = _create_incident_with_ai(client, db_session, auth_headers, ai_issue_type=2)
        client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        count = db_session.query(RiskAssessment).filter(
            RiskAssessment.incident_id == inc_id
        ).count()
        assert count == 1

    def test_repeated_call_produces_same_result(self, client, db_session, auth_headers):
        """TEST B6: Repeated calls are deterministic (same result)."""
        inc_id = _create_incident_with_ai(client, db_session, auth_headers, ai_issue_type=3)
        r1 = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers).json()
        r2 = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers).json()
        assert r1["risk_score"] == r2["risk_score"]
        assert r1["risk_level"] == r2["risk_level"]
        assert r1["priority"]   == r2["priority"]

    def test_unauthenticated_request_is_rejected(self, client, db_session, auth_headers):
        """TEST B7: No auth header → 401 or 403."""
        inc_id = _create_incident_with_ai(client, db_session, auth_headers)
        resp = client.post(f"/incidents/{inc_id}/risk-assessment")  # No token
        assert resp.status_code in (401, 403)

    def test_risk_score_is_within_valid_range(self, client, db_session, auth_headers):
        """TEST B8: Risk score in response is within [0, 100]."""
        inc_id = _create_incident_with_ai(client, db_session, auth_headers, ai_issue_type=1, ai_confidence=1.0, citizen_rating=10)
        body = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers).json()
        assert 0 <= body["risk_score"] <= 100

    def test_risk_level_maps_to_correct_priority(self, client, db_session, auth_headers):
        """TEST B9: risk_level and priority are consistent."""
        mapping = {"LOW": "LOW", "MEDIUM": "NORMAL", "HIGH": "HIGH", "CRITICAL": "URGENT"}
        inc_id = _create_incident_with_ai(client, db_session, auth_headers, ai_issue_type=4)
        body = client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers).json()
        assert body["priority"] == mapping[body["risk_level"]]

    def test_incident_status_updated_to_risk_assessed(self, client, db_session, auth_headers):
        """TEST B10: Incident status is updated to RISK_ASSESSED."""
        inc_id = _create_incident_with_ai(client, db_session, auth_headers, ai_issue_type=5)
        client.post(f"/incidents/{inc_id}/risk-assessment", headers=auth_headers)
        db_session.expire_all()
        inc = db_session.query(Incident).filter(Incident.id == inc_id).first()
        assert inc.status == "RISK_ASSESSED"
