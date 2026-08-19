from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..database.base import Base

class ResolutionFeedback(Base):
    __tablename__ = "resolution_feedbacks"
    __table_args__ = (
        UniqueConstraint("incident_id", "user_id", name="uq_incident_user_feedback"),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    satisfied = Column(String(10), nullable=False)  # YES or NO
    rating = Column(Integer, nullable=True)  # 1 to 5 optional rating
    feedback_text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    incident = relationship("Incident", back_populates="feedbacks")
    user = relationship("User")
