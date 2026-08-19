import logging
from typing import Optional
from sqlalchemy.orm import Session
from ..models.sos_event import SOSEvent

logger = logging.getLogger(__name__)

class SOSService:
    """Placeholder service interface for SOS Emergency Dispatch (Phase 10)."""
    @staticmethod
    def trigger_emergency_event(
        db: Session,
        incident_id: Optional[int] = None,
        trigger_reason: Optional[str] = "Manual SOS Trigger",
        risk_score: Optional[float] = 100.0,
    ) -> SOSEvent:
        sos_event = SOSEvent(
            incident_id=incident_id,
            trigger_reason=trigger_reason,
            risk_score=risk_score,
            status="ACTIVE",
        )
        db.add(sos_event)
        db.commit()
        db.refresh(sos_event)
        logger.warning(f"[Phase 1 Placeholder] Emergency SOS event created: ID={sos_event.id}")
        return sos_event
