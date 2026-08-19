"""Phase 6 — RiskAssessment database model.

Stores the calculated risk assessment for a civic incident.
One risk assessment per incident (enforced by UniqueConstraint).
"""

from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from ..database.base import Base


class RiskAssessment(Base):
    """Stores Phase 6 risk assessment result for a given incident.

    Fields
    ------
    incident_id       : FK to incidents table (one-to-one by UniqueConstraint).
    risk_score        : Calculated score 0–100 (float, 2 dp).
    risk_level        : LOW | MEDIUM | HIGH | CRITICAL.
    priority          : LOW | NORMAL | HIGH | URGENT.
    crisis_class      : Raw class key (e.g. 'open_manhole') used in calculation.
    crisis_severity   : Baseline severity score for this crisis class (0–100).
    ai_confidence     : AI confidence used in calculation (0.0–1.0).
    citizen_rating    : Citizen rating used (0–10).
    location_available: Whether GPS was available (True/False).
    explanation       : Deterministic human-readable risk explanation.
    calculated_at     : UTC timestamp of calculation.
    """

    __tablename__ = "risk_assessments"
    __table_args__ = (
        UniqueConstraint("incident_id", name="uq_risk_assessment_incident"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign key — one risk assessment per incident
    incident_id = Column(
        Integer,
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Core risk outputs
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False, index=True)
    priority = Column(String(20), nullable=False, index=True)

    # Inputs captured at calculation time (for auditability)
    crisis_class = Column(String(50), nullable=False)
    crisis_severity = Column(Float, nullable=False)
    ai_confidence = Column(Float, nullable=False)
    citizen_rating = Column(Integer, nullable=False)
    location_available = Column(Boolean, nullable=False)

    # Deterministic human-readable explanation
    explanation = Column(Text, nullable=False)

    # Timestamp of calculation
    calculated_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationship back to incident
    incident = relationship("Incident", back_populates="risk_assessment")
