from enum import Enum, IntEnum
from typing import Dict

class IncidentStatus(str, Enum):
    DRAFT = "DRAFT"              # Phase 3: offline-drafted, not yet submitted
    CREATED = "CREATED"          # Phase 2: submitted directly to backend
    PENDING_SYNC = "PENDING_SYNC"  # Phase 3: awaiting offline sync
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    AI_PROCESSING = "AI_PROCESSING"
    COMMUNITY_VERIFICATION = "COMMUNITY_VERIFICATION"
    RISK_ASSESSED = "RISK_ASSESSED"
    UNASSIGNED = "UNASSIGNED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    FAILED = "FAILED"


class LocationStatus(str, Enum):
    """GPS availability status at the time of incident creation."""
    AVAILABLE = "AVAILABLE"      # GPS coordinates were captured successfully
    UNAVAILABLE = "UNAVAILABLE"  # GPS was unavailable; coordinates are null

class IncidentLifecycle(str, Enum):
    CREATED = "CREATED"
    ROUTED = "ROUTED"
    IN_PROGRESS = "IN_PROGRESS"
    VERIFIED = "VERIFIED"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AITaxonomyClass(IntEnum):
    # Phase 1 / 4 Active Classes
    POTHOLE = 0
    OPEN_MANHOLE = 1
    GARBAGE = 2
    
    # Future Phase Classes
    FLOODING = 3
    BROKEN_STREETLIGHT = 4
    WATER_LEAKAGE = 5

AI_TAXONOMY_MAP: Dict[int, str] = {
    AITaxonomyClass.POTHOLE: "pothole",
    AITaxonomyClass.OPEN_MANHOLE: "open_manhole",
    AITaxonomyClass.GARBAGE: "garbage",
    AITaxonomyClass.FLOODING: "flooding",
    AITaxonomyClass.BROKEN_STREETLIGHT: "broken_streetlight",
    AITaxonomyClass.WATER_LEAKAGE: "water_leakage",
}

# Phase 6: Map Phase 5 display names → RISK_CONFIG crisis_severity keys.
# This allows RiskEngineService to look up severity without string parsing.
DISPLAY_NAME_TO_CLASS_KEY: Dict[str, str] = {
    "Pothole / Road Damage": "pothole",
    "Open Manhole": "open_manhole",
    "Garbage Accumulation": "garbage",
    "Flooding / Waterlogging": "flooding",
    "Broken Streetlight": "broken_streetlight",
    "Water Leakage": "water_leakage",
}

# Phase 6: Reverse map — raw class key → AITaxonomyClass int.
CLASS_KEY_TO_TAXONOMY: Dict[str, int] = {
    v: k for k, v in AI_TAXONOMY_MAP.items()
}

# Phase 9: Default department mapping per issue type key
DEFAULT_DEPARTMENT_MAPPINGS: Dict[str, str] = {
    "pothole": "Roads / Public Works Department",
    "open_manhole": "Roads / Public Works / Sewer Department",
    "garbage": "Sanitation / Waste Management Department",
    "flooding": "Storm Water / Disaster Management Department",
    "broken_streetlight": "Electrical / Municipal Department",
    "water_leakage": "Water Supply / Water Department",
}


class IncidentPriority(str, Enum):
    """Phase 6: Incident priority derived from Risk Level."""
    LOW    = "LOW"
    NORMAL = "NORMAL"
    HIGH   = "HIGH"
    URGENT = "URGENT"

class UserRole(str, Enum):
    CITIZEN = "citizen"
    COMMUNITY_LEAD = "community_lead"
    MUNICIPAL_STAFF = "municipal_staff"
    EMERGENCY_RESPONDER = "emergency_responder"
    ADMIN = "admin"

class VerificationResponse(str, Enum):
    YES = "YES"
    NO = "NO"
    UNKNOWN = "UNKNOWN"

class NotificationType(str, Enum):
    COMMUNITY_ALERT = "COMMUNITY_ALERT"
    STATUS_UPDATE = "STATUS_UPDATE"
    EMERGENCY_BROADCAST = "EMERGENCY_BROADCAST"
    POINTS_AWARDED = "POINTS_AWARDED"

class NotificationStatus(str, Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"

class SOSStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RESPONDED = "RESPONDED"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"
