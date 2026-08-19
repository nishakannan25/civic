"""Phase 6 — Pydantic schemas for Risk Assessment API responses."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class RiskAssessmentResponse(BaseModel):
    """Full risk assessment result returned by POST /incidents/{id}/risk-assessment."""

    model_config = ConfigDict(from_attributes=True)

    incident_id: int = Field(..., description="ID of the assessed incident")
    risk_score: float = Field(
        ..., ge=0.0, le=100.0,
        description="Calculated risk score (0–100, higher = more urgent)",
        example=78.5,
    )
    risk_level: str = Field(
        ...,
        description="Categorical risk level: LOW | MEDIUM | HIGH | CRITICAL",
        example="HIGH",
    )
    priority: str = Field(
        ...,
        description="Incident priority: LOW | NORMAL | HIGH | URGENT",
        example="HIGH",
    )
    crisis_class: str = Field(
        ...,
        description="Raw crisis class key used in calculation (e.g. 'open_manhole')",
        example="open_manhole",
    )
    crisis_severity: float = Field(
        ..., ge=0.0, le=100.0,
        description="Baseline severity for this crisis class (0–100)",
        example=95.0,
    )
    ai_confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="AI confidence used in calculation (0.0–1.0)",
        example=0.94,
    )
    citizen_rating: int = Field(
        ..., ge=0, le=10,
        description="Citizen severity rating used (0–10)",
        example=9,
    )
    location_available: bool = Field(
        ...,
        description="Whether GPS location was available for this incident",
        example=True,
    )
    explanation: str = Field(
        ...,
        description="Deterministic human-readable explanation of the risk assessment",
        example=(
            "High-risk incident. The detected category (Open Manhole) has a very high "
            "baseline severity. AI confidence is strong (94%). Citizen-reported severity "
            "is high (9/10). GPS location is available."
        ),
    )
    calculated_at: datetime = Field(
        ...,
        description="UTC timestamp when this assessment was calculated",
    )


class RiskAssessmentSummary(BaseModel):
    """Slim risk summary embedded in incident responses (Phase 6)."""

    risk_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    risk_level: Optional[str] = None
    priority: Optional[str] = None
    explanation: Optional[str] = None
    calculated_at: Optional[datetime] = None
