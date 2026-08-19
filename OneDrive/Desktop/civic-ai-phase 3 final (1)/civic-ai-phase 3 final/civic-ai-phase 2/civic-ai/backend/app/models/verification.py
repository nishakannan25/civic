from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database.base import Base

class Verification(Base):
    __tablename__ = "verifications"
    __table_args__ = (
        UniqueConstraint("incident_id", "user_id", name="uq_incident_user_verification"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    response = Column(String(20), nullable=False)  # YES, NO, UNKNOWN
    rating = Column(Integer, nullable=True)  # 1 to 10 severity rating for YES responses
    distance_from_incident = Column(Float, nullable=True)  # in meters
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    incident = relationship("Incident", back_populates="verifications")
    user = relationship("User", back_populates="verifications")

