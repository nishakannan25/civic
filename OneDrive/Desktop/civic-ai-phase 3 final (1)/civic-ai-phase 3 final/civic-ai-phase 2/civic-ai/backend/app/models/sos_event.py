from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..database.base import Base

class SOSEvent(Base):
    __tablename__ = "sos_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=True, index=True)
    trigger_reason = Column(String(255), nullable=True)
    risk_score = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE")
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime, nullable=True)

    # Relationships
    incident = relationship("Incident", back_populates="sos_events")
