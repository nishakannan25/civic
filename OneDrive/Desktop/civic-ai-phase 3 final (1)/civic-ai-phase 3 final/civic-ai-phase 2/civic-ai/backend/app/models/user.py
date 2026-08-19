from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from ..database.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="citizen")
    points = Column(Integer, nullable=False, default=0)
    reputation_score = Column(Float, nullable=False, default=5.0)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    # Relationships
    incidents = relationship("Incident", foreign_keys="[Incident.user_id]", back_populates="user", cascade="all, delete-orphan")

    verifications = relationship("Verification", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="recipient_user", cascade="all, delete-orphan")
    point_transactions = relationship("PointTransaction", back_populates="user", cascade="all, delete-orphan")
