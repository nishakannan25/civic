from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database.base import Base

class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        UniqueConstraint("user_id", "client_incident_id", name="uq_user_client_incident"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(512), nullable=True)
    # Phase 2: latitude/longitude are nullable when GPS is unavailable
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    gps_accuracy = Column(Float, nullable=True)
    # Phase 2: tracks whether GPS was available during incident creation
    location_status = Column(String(20), nullable=False, default="UNAVAILABLE", index=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    citizen_rating = Column(Integer, nullable=True)
    ai_issue_type = Column(Integer, nullable=True, index=True)
    ai_confidence = Column(Float, nullable=True)
    ai_severity = Column(Integer, nullable=True)
    community_yes = Column(Integer, nullable=False, default=0)
    community_no = Column(Integer, nullable=False, default=0)
    community_unknown = Column(Integer, nullable=False, default=0)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(50), nullable=True)
    status = Column(String(50), nullable=False, default="DRAFT", index=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Phase 3: Client-side idempotency ID and upload timestamp
    client_incident_id = Column(String(64), nullable=True, index=True)
    uploaded_at = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))
    image_hash = Column(String(64), nullable=True, index=True)

    # Phase 9: Routing and Resolution fields
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    routing_status = Column(String(50), nullable=False, default="UNASSIGNED", index=True)
    assigned_at = Column(DateTime, nullable=True)
    assigned_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolution_note = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="incidents")
    department = relationship("Department", back_populates="incidents")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])
    resolved_by_user = relationship("User", foreign_keys=[resolved_by])
    verifications = relationship("Verification", back_populates="incident", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="incident", cascade="all, delete-orphan")
    point_transactions = relationship("PointTransaction", back_populates="incident")
    sos_events = relationship("SOSEvent", back_populates="incident", cascade="all, delete-orphan")
    # Phase 6: One-to-one risk assessment (uselist=False)
    risk_assessment = relationship("RiskAssessment", back_populates="incident", uselist=False, cascade="all, delete-orphan")
    # Phase 10A: Resolution feedbacks
    feedbacks = relationship("ResolutionFeedback", back_populates="incident", cascade="all, delete-orphan")


