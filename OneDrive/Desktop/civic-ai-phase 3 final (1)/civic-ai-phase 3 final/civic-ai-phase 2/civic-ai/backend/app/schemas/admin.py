from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    total_incidents: int
    active_incidents: int
    critical_incidents: int
    assigned_incidents: int
    in_progress: int
    resolved: int
    closed: int
    issue_distribution: Dict[str, int]
    risk_distribution: Dict[str, int]

class IncidentAssignmentRequest(BaseModel):
    department_id: int

class IncidentStatusUpdateRequest(BaseModel):
    status: str
    resolution_note: Optional[str] = None

class MapIncidentItem(BaseModel):
    id: int
    issue_type: str
    risk_level: Optional[str] = None
    status: str
    department_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_status: str

    class Config:
        from_attributes = True

class RoutingResultResponse(BaseModel):
    incident_id: int
    issue_type: str
    risk_level: Optional[str] = None
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    routing_status: str
    message: Optional[str] = None
