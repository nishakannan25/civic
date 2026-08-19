"""Phase 3 Pydantic schemas for civic incident reporting.

Changes from Phase 2:
- client_incident_id support for offline synchronization idempotency
- uploaded_at field tracking sync/upload completion time
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, model_validator
from ..core.constants import IncidentStatus, RiskLevel, LocationStatus


class IncidentCreateForm:
    """
    Represents validated form fields from a multipart/form-data incident submission.
    Not a Pydantic model — instantiated manually in the API route from Form() params.
    """
    def __init__(
        self,
        citizen_rating: int,
        location_status: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        gps_accuracy: Optional[float] = None,
        timestamp: Optional[str] = None,
        client_incident_id: Optional[str] = None,
    ):
        self.citizen_rating = citizen_rating
        self.location_status = location_status
        self.latitude = latitude
        self.longitude = longitude
        self.gps_accuracy = gps_accuracy
        self.timestamp = timestamp
        self.client_incident_id = client_incident_id


class IncidentCreate(BaseModel):
    """Legacy JSON-based schema kept for backward compat and testing."""
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    gps_accuracy: Optional[float] = Field(None, ge=0.0)
    image_url: Optional[str] = Field(None, max_length=512)
    citizen_rating: Optional[int] = Field(None, ge=0, le=10, description="Citizen perceived severity (0–10)")
    location_status: str = Field(default="UNAVAILABLE", description="AVAILABLE or UNAVAILABLE")
    client_incident_id: Optional[str] = Field(None, max_length=64, description="Unique client-generated incident ID")


class IncidentUpdate(BaseModel):
    status: Optional[IncidentStatus] = None
    citizen_rating: Optional[int] = Field(None, ge=0, le=10)
    image_url: Optional[str] = Field(None, max_length=512)


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    gps_accuracy: Optional[float] = None
    location_status: str = "UNAVAILABLE"
    timestamp: datetime
    citizen_rating: Optional[int] = None
    ai_issue_type: Optional[int] = None
    ai_confidence: Optional[float] = None
    ai_severity: Optional[int] = None
    community_yes: int
    community_no: int
    community_unknown: int
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    status: str
    client_incident_id: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    routing_status: Optional[str] = "UNASSIGNED"
    assigned_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


    @property
    def reference_id(self) -> str:
        """Human-readable incident reference ID for the mobile success screen."""
        ts = self.created_at
        return f"CIV-{ts.year}-{self.id:06d}"


class IncidentCreateResponse(BaseModel):
    """Response returned after successful incident creation or idempotent match."""
    id: int
    reference_id: str
    status: str
    citizen_rating: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_status: str
    client_incident_id: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    message: str = "Incident created successfully"


class IncidentListResponse(BaseModel):
    total: int
    items: List[IncidentResponse]
