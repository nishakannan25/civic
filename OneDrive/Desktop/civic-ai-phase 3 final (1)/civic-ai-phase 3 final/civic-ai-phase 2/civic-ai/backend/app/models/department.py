from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
from ..database.base import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    issue_types = Column(Text, nullable=False)  # JSON-encoded array or comma-separated issue types
    service_area = Column(Text, nullable=True)  # JSON-encoded geo polygon or municipal zone
    contact_information = Column(Text, nullable=True)  # JSON-encoded contact info (email, phone, dispatch)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    incidents = relationship("Incident", back_populates="department")

