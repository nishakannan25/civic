"""Phase 6 — Risk Engine Service.

Deterministic, configurable incident risk assessment.

Architecture
------------
This module is the ONLY place where risk scoring logic lives.
The API route (`incidents.py`) calls `RiskEngineService.calculate()`
and receives a fully-formed `RiskAssessment` ORM object.

No risk logic belongs in:
  - API routes
  - Database models
  - Mobile widgets
  - AI inference service

Scoring Formula
---------------
risk_score = (
      (crisis_severity / max_severity)   * SEVERITY_WEIGHT
    + ai_confidence                       * CONFIDENCE_WEIGHT
    + (citizen_rating / 10)              * CITIZEN_RATING_WEIGHT
    + location_component                 * LOCATION_WEIGHT
) * 100

Clamped to [0.0, 100.0], rounded to 2 decimal places.

Configuration
-------------
All weights and thresholds are read from `settings.RISK_CONFIG` (JSON).
Defaults are defined in `core/config.py` — do NOT hardcode elsewhere.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from ..core.config import settings
from ..core.constants import (
    RiskLevel,
    IncidentPriority,
    AI_TAXONOMY_MAP,
    DISPLAY_NAME_TO_CLASS_KEY,
)
from ..models.incident import Incident
from ..models.risk_assessment import RiskAssessment

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Fallback defaults used if RISK_CONFIG cannot be parsed from settings
# ─────────────────────────────────────────────────────────────────────────────

_DEFAULT_CRISIS_SEVERITY: Dict[str, float] = {
    "open_manhole":       95.0,
    "flooding":           90.0,
    "pothole":            70.0,
    "water_leakage":      60.0,
    "broken_streetlight": 50.0,
    "garbage":            40.0,
}

_DEFAULT_WEIGHTS: Dict[str, float] = {
    "severity":       0.40,
    "confidence":     0.30,
    "citizen_rating": 0.20,
    "location":       0.10,
}

_DEFAULT_THRESHOLDS: Dict[str, float] = {
    "low_max":    25.0,
    "medium_max": 50.0,
    "high_max":   75.0,
}

_DEFAULT_PRIORITY_MAP: Dict[str, str] = {
    "LOW":      IncidentPriority.LOW.value,
    "MEDIUM":   IncidentPriority.NORMAL.value,
    "HIGH":     IncidentPriority.HIGH.value,
    "CRITICAL": IncidentPriority.URGENT.value,
}

# Maximum possible crisis severity (used for normalisation)
_MAX_CRISIS_SEVERITY: float = 100.0

# AI confidence threshold below which "weak confidence" language is used
_WEAK_CONFIDENCE_THRESHOLD: float = 0.50
_STRONG_CONFIDENCE_THRESHOLD: float = 0.80


def _load_risk_config() -> Dict[str, Any]:
    """Parse RISK_CONFIG from settings. Returns merged defaults on parse failure."""
    try:
        raw = settings.RISK_CONFIG
        if raw:
            cfg = json.loads(raw)
            return {
                "crisis_severity": cfg.get("crisis_severity", _DEFAULT_CRISIS_SEVERITY),
                "weights":         cfg.get("weights",         _DEFAULT_WEIGHTS),
                "thresholds":      cfg.get("thresholds",      _DEFAULT_THRESHOLDS),
                "priority_map":    cfg.get("priority_map",    _DEFAULT_PRIORITY_MAP),
            }
    except (json.JSONDecodeError, TypeError, AttributeError) as exc:
        logger.warning("Could not parse RISK_CONFIG from settings, using defaults: %s", exc)

    return {
        "crisis_severity": _DEFAULT_CRISIS_SEVERITY,
        "weights":         _DEFAULT_WEIGHTS,
        "thresholds":      _DEFAULT_THRESHOLDS,
        "priority_map":    _DEFAULT_PRIORITY_MAP,
    }


class RiskEngineService:
    """Phase 6 Risk Engine — deterministic, configurable risk assessment.

    Public API
    ----------
    RiskEngineService.calculate(incident, db)
        → Compute, upsert into DB, return RiskAssessment ORM object.

    RiskEngineService.calculate_score(crisis_class, ai_confidence, citizen_rating, location_available)
        → Pure function (no DB). Returns a dict with all intermediate values.

    RiskEngineService.determine_risk_level(risk_score)
        → Map numeric score to RiskLevel string.

    RiskEngineService.determine_priority(risk_level)
        → Map RiskLevel string to IncidentPriority string.
    """

    # ─────────────────────────────────────────────────────────────────────────
    # PURE CALCULATION — No database, no side effects
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def calculate_score(
        crisis_class: str,
        ai_confidence: float,
        citizen_rating: int,
        location_available: bool,
    ) -> Dict[str, Any]:
        """Calculate risk score components from validated inputs.

        Parameters
        ----------
        crisis_class       : Raw class key (e.g. 'open_manhole', 'pothole').
        ai_confidence      : AI confidence in [0.0, 1.0].
        citizen_rating     : Citizen rating in [0, 10].
        location_available : True if GPS coordinates are available.

        Returns
        -------
        dict with keys:
            risk_score (float, 0–100)
            risk_level (str)
            priority (str)
            crisis_severity (float)
            explanation (str)
            normalized_severity (float)
            normalized_confidence (float)
            normalized_rating (float)
            location_component (float)
            weights (dict)
        """
        cfg = _load_risk_config()
        crisis_severity_map: Dict[str, float] = cfg["crisis_severity"]
        weights: Dict[str, float] = cfg["weights"]

        # ── Input Validation ─────────────────────────────────────────────────
        if crisis_class not in crisis_severity_map:
            known = list(crisis_severity_map.keys())
            raise ValueError(
                f"Unknown crisis class '{crisis_class}'. "
                f"Supported classes: {known}."
            )
        if not isinstance(ai_confidence, (int, float)) or not (0.0 <= float(ai_confidence) <= 1.0):
            raise ValueError(
                f"ai_confidence must be in [0.0, 1.0], got {ai_confidence!r}."
            )
        if not isinstance(citizen_rating, int) or not (0 <= citizen_rating <= 10):
            raise ValueError(
                f"citizen_rating must be an integer in [0, 10], got {citizen_rating!r}."
            )

        ai_confidence = float(ai_confidence)

        # ── Component Calculation ────────────────────────────────────────────
        crisis_severity: float = float(crisis_severity_map[crisis_class])
        normalized_severity: float  = crisis_severity / _MAX_CRISIS_SEVERITY
        normalized_confidence: float = ai_confidence
        normalized_rating: float    = citizen_rating / 10.0
        location_component: float   = 1.0 if location_available else 0.0

        w_severity  = float(weights.get("severity",       0.40))
        w_confidence = float(weights.get("confidence",    0.30))
        w_rating    = float(weights.get("citizen_rating", 0.20))
        w_location  = float(weights.get("location",       0.10))

        raw_score = (
              normalized_severity   * w_severity
            + normalized_confidence * w_confidence
            + normalized_rating     * w_rating
            + location_component    * w_location
        )

        risk_score = round(min(max(raw_score * 100.0, 0.0), 100.0), 2)

        # ── Risk Level & Priority ────────────────────────────────────────────
        risk_level = RiskEngineService.determine_risk_level(risk_score, cfg)
        priority   = RiskEngineService.determine_priority(risk_level, cfg)

        # ── Explanation ──────────────────────────────────────────────────────
        explanation = RiskEngineService._build_explanation(
            crisis_class=crisis_class,
            crisis_severity=crisis_severity,
            ai_confidence=ai_confidence,
            citizen_rating=citizen_rating,
            location_available=location_available,
            risk_level=risk_level,
            risk_score=risk_score,
        )

        return {
            "risk_score":           risk_score,
            "risk_level":           risk_level,
            "priority":             priority,
            "crisis_severity":      crisis_severity,
            "explanation":          explanation,
            "normalized_severity":  normalized_severity,
            "normalized_confidence": normalized_confidence,
            "normalized_rating":    normalized_rating,
            "location_component":   location_component,
            "weights":              {
                "severity":       w_severity,
                "confidence":     w_confidence,
                "citizen_rating": w_rating,
                "location":       w_location,
            },
        }

    # ─────────────────────────────────────────────────────────────────────────
    # RISK LEVEL & PRIORITY MAPPING
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def determine_risk_level(
        risk_score: float,
        cfg: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Map numeric risk score (0–100) to categorical risk level.

        Uses configurable thresholds from RISK_CONFIG.
        """
        if cfg is None:
            cfg = _load_risk_config()
        thresholds = cfg.get("thresholds", _DEFAULT_THRESHOLDS)

        low_max    = float(thresholds.get("low_max",    25.0))
        medium_max = float(thresholds.get("medium_max", 50.0))
        high_max   = float(thresholds.get("high_max",   75.0))

        if risk_score < low_max:
            return RiskLevel.LOW.value
        elif risk_score < medium_max:
            return RiskLevel.MEDIUM.value
        elif risk_score < high_max:
            return RiskLevel.HIGH.value
        else:
            return RiskLevel.CRITICAL.value

    @staticmethod
    def determine_priority(
        risk_level: str,
        cfg: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Map risk level to incident priority using configurable priority_map."""
        if cfg is None:
            cfg = _load_risk_config()
        priority_map = cfg.get("priority_map", _DEFAULT_PRIORITY_MAP)
        return priority_map.get(risk_level, IncidentPriority.NORMAL.value)

    # ─────────────────────────────────────────────────────────────────────────
    # DETERMINISTIC EXPLANATION BUILDER
    # ─────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _build_explanation(
        crisis_class: str,
        crisis_severity: float,
        ai_confidence: float,
        citizen_rating: int,
        location_available: bool,
        risk_level: str,
        risk_score: float,
    ) -> str:
        """Build a deterministic, human-readable explanation from actual input values.

        This is purely rule-based — no LLM, no randomness.
        """
        # Crisis class display label
        crisis_display_map = {
            "open_manhole":       "Open Manhole",
            "flooding":           "Flooding / Waterlogging",
            "pothole":            "Pothole / Road Damage",
            "water_leakage":      "Water Leakage",
            "broken_streetlight": "Broken Streetlight",
            "garbage":            "Garbage Accumulation",
        }
        display_name = crisis_display_map.get(crisis_class, crisis_class.replace("_", " ").title())

        # Severity qualifier
        if crisis_severity >= 85:
            severity_label = "very high"
        elif crisis_severity >= 65:
            severity_label = "high"
        elif crisis_severity >= 45:
            severity_label = "medium"
        else:
            severity_label = "lower"

        # Confidence qualifier
        if ai_confidence >= _STRONG_CONFIDENCE_THRESHOLD:
            confidence_label = "strong"
        elif ai_confidence >= _WEAK_CONFIDENCE_THRESHOLD:
            confidence_label = "moderate"
        else:
            confidence_label = "weak"

        # Citizen rating qualifier
        if citizen_rating >= 8:
            rating_label = "high"
        elif citizen_rating >= 5:
            rating_label = "moderate"
        else:
            rating_label = "low"

        # Location statement
        location_stmt = (
            "GPS location is available, aiding field response."
            if location_available
            else "GPS location is unavailable; response will rely on manual address lookup."
        )

        # Risk level preamble
        preamble_map = {
            RiskLevel.LOW.value:      "This incident has a low risk profile.",
            RiskLevel.MEDIUM.value:   "This incident requires attention.",
            RiskLevel.HIGH.value:     "This is a high-risk incident requiring prompt action.",
            RiskLevel.CRITICAL.value: "This is a CRITICAL incident requiring immediate response.",
        }
        preamble = preamble_map.get(risk_level, "Risk assessment complete.")

        explanation = (
            f"{preamble} "
            f"The detected category ({display_name}) has a {severity_label} baseline severity "
            f"({crisis_severity:.0f}/100). "
            f"AI confidence is {confidence_label} ({ai_confidence * 100:.0f}%). "
            f"Citizen-reported severity is {rating_label} ({citizen_rating}/10). "
            f"{location_stmt} "
            f"Calculated risk score: {risk_score:.1f}/100."
        )
        return explanation

    # ─────────────────────────────────────────────────────────────────────────
    # DATABASE INTEGRATION — Upsert RiskAssessment
    # ─────────────────────────────────────────────────────────────────────────

    @classmethod
    def calculate(
        cls,
        incident: Incident,
        db: Session,
    ) -> RiskAssessment:
        """Compute risk assessment for an incident and persist/update the result.

        Parameters
        ----------
        incident : Incident ORM object with valid ai_issue_type, ai_confidence,
                   citizen_rating, and location_status fields.
        db       : Active SQLAlchemy session.

        Returns
        -------
        RiskAssessment ORM object (newly created or updated).

        Raises
        ------
        ValueError  : If incident is missing required AI or citizen input fields.
        ValueError  : If ai_confidence or citizen_rating is out of valid range.
        """
        # ── Validate AI result is present ─────────────────────────────────
        if incident.ai_issue_type is None:
            raise ValueError(
                f"Incident {incident.id} has no AI inference result (ai_issue_type is None). "
                "Run Phase 5 AI inference before requesting risk assessment."
            )
        if incident.ai_confidence is None:
            raise ValueError(
                f"Incident {incident.id} has no AI confidence value. "
                "Run Phase 5 AI inference before requesting risk assessment."
            )

        # ── Resolve crisis class key ─────────────────────────────────────
        class_key = AI_TAXONOMY_MAP.get(incident.ai_issue_type)
        if class_key is None:
            raise ValueError(
                f"ai_issue_type '{incident.ai_issue_type}' does not map to a known crisis class."
            )

        # ── Resolve citizen rating ────────────────────────────────────────
        citizen_rating = incident.citizen_rating
        if citizen_rating is None:
            citizen_rating = 0  # Safe default when citizen_rating not provided
        if not (0 <= citizen_rating <= 10):
            raise ValueError(
                f"citizen_rating {citizen_rating} is out of valid range [0, 10]."
            )

        # ── Location availability ─────────────────────────────────────────
        location_available: bool = (
            incident.location_status == "AVAILABLE"
            and incident.latitude is not None
            and incident.longitude is not None
        )

        # ── Run pure calculation ──────────────────────────────────────────
        result = cls.calculate_score(
            crisis_class=class_key,
            ai_confidence=incident.ai_confidence,
            citizen_rating=citizen_rating,
            location_available=location_available,
        )

        now = datetime.now(timezone.utc)

        # ── Upsert into risk_assessments table ───────────────────────────
        existing: Optional[RiskAssessment] = (
            db.query(RiskAssessment)
            .filter(RiskAssessment.incident_id == incident.id)
            .first()
        )

        if existing:
            # Update existing assessment with new values (deterministic recalculation)
            existing.risk_score        = result["risk_score"]
            existing.risk_level        = result["risk_level"]
            existing.priority          = result["priority"]
            existing.crisis_class      = class_key
            existing.crisis_severity   = result["crisis_severity"]
            existing.ai_confidence     = float(incident.ai_confidence)
            existing.citizen_rating    = citizen_rating
            existing.location_available = location_available
            existing.explanation       = result["explanation"]
            existing.calculated_at     = now
            db.commit()
            db.refresh(existing)
            assessment = existing
        else:
            # Create new assessment
            assessment = RiskAssessment(
                incident_id        = incident.id,
                risk_score         = result["risk_score"],
                risk_level         = result["risk_level"],
                priority           = result["priority"],
                crisis_class       = class_key,
                crisis_severity    = result["crisis_severity"],
                ai_confidence      = float(incident.ai_confidence),
                citizen_rating     = citizen_rating,
                location_available = location_available,
                explanation        = result["explanation"],
                calculated_at      = now,
            )
            db.add(assessment)
            db.commit()
            db.refresh(assessment)

        # ── Mirror risk_score and risk_level back onto the Incident record ─
        incident.risk_score = result["risk_score"]
        incident.risk_level = result["risk_level"]
        incident.status     = "RISK_ASSESSED"
        db.commit()
        db.refresh(incident)

        logger.info(
            "Risk assessment for incident %d: score=%.2f level=%s priority=%s",
            incident.id,
            result["risk_score"],
            result["risk_level"],
            result["priority"],
        )

        return assessment
