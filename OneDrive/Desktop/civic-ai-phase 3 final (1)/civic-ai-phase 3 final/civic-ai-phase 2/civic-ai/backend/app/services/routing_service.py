import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from ..models.department import Department
from ..models.incident import Incident
from ..models.user import User
from ..core.constants import (
    DEFAULT_DEPARTMENT_MAPPINGS,
    AI_TAXONOMY_MAP,
    IncidentStatus,
)
from ..core.exceptions import EntityNotFoundException, BadRequestException, ForbiddenException

logger = logging.getLogger(__name__)

# Valid state transitions for incident status
VALID_STATUS_TRANSITIONS = {
    "DRAFT": ["CREATED", "PENDING_SYNC"],
    "PENDING_SYNC": ["CREATED"],
    "CREATED": ["AI_PROCESSING", "COMMUNITY_VERIFICATION", "RISK_ASSESSED", "UNASSIGNED", "ASSIGNED"],
    "AI_PROCESSING": ["COMMUNITY_VERIFICATION", "RISK_ASSESSED", "UNASSIGNED", "ASSIGNED"],
    "COMMUNITY_VERIFICATION": ["RISK_ASSESSED", "UNASSIGNED", "ASSIGNED"],
    "RISK_ASSESSED": ["UNASSIGNED", "ASSIGNED", "IN_PROGRESS"],
    "UNASSIGNED": ["ASSIGNED", "IN_PROGRESS", "CLOSED"],
    "ASSIGNED": ["IN_PROGRESS", "UNASSIGNED", "RESOLVED", "CLOSED"],
    "IN_PROGRESS": ["RESOLVED", "ASSIGNED", "UNASSIGNED", "CLOSED"],
    "RESOLVED": ["CLOSED", "IN_PROGRESS"],
    "CLOSED": [],
}


class CivicRoutingService:

    @staticmethod
    def seed_default_departments(db: Session):
        """Seed default 6 municipal departments if not already present."""
        for issue_type, dept_name in DEFAULT_DEPARTMENT_MAPPINGS.items():
            existing = db.query(Department).filter(Department.name == dept_name).first()
            if not existing:
                dept = Department(
                    name=dept_name,
                    description=f"Department responsible for managing {issue_type.replace('_', ' ')} issues.",
                    issue_types=json.dumps([issue_type]),
                    is_active=True,
                )
                db.add(dept)
        db.commit()

    @staticmethod
    def get_department_for_issue_type(db: Session, issue_type_str: str) -> Optional[Department]:
        """Find active department matching issue type."""
        dept_name = DEFAULT_DEPARTMENT_MAPPINGS.get(issue_type_str)
        if not dept_name:
            return None
        return (
            db.query(Department)
            .filter(Department.name == dept_name, Department.is_active == True)
            .first()
        )

    @staticmethod
    def route_incident(db: Session, incident_id: int) -> Dict[str, Any]:
        """
        Automatic Routing logic:
        1. Read incident issue type.
        2. Determine department.
        3. Verify department exists and is active.
        4. Assign incident and store routing info.
        5. Return routing result.
        """
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise EntityNotFoundException("Incident", incident_id)

        # Determine issue type string from AI taxonomy index
        issue_type_str = None
        if incident.ai_issue_type is not None:
            issue_type_str = AI_TAXONOMY_MAP.get(incident.ai_issue_type)

        if not issue_type_str or issue_type_str == "unknown":
            incident.routing_status = IncidentStatus.UNASSIGNED.value
            db.commit()
            return {
                "incident_id": incident.id,
                "issue_type": issue_type_str or "unknown",
                "risk_level": incident.risk_level,
                "department_id": None,
                "department_name": None,
                "routing_status": IncidentStatus.UNASSIGNED.value,
                "message": "Unable to determine appropriate department.",
            }

        department = CivicRoutingService.get_department_for_issue_type(db, issue_type_str)
        if not department:
            # Department not found or inactive
            incident.routing_status = IncidentStatus.UNASSIGNED.value
            db.commit()
            return {
                "incident_id": incident.id,
                "issue_type": issue_type_str,
                "risk_level": incident.risk_level,
                "department_id": None,
                "department_name": None,
                "routing_status": IncidentStatus.UNASSIGNED.value,
                "message": f"No active department available for issue type '{issue_type_str}'.",
            }

        # Perform automatic assignment
        now = datetime.now(timezone.utc)
        incident.department_id = department.id
        incident.routing_status = IncidentStatus.ASSIGNED.value
        incident.status = IncidentStatus.ASSIGNED.value
        incident.assigned_at = now
        incident.updated_at = now
        db.commit()
        db.refresh(incident)

        return {
            "incident_id": incident.id,
            "issue_type": issue_type_str,
            "risk_level": incident.risk_level,
            "department_id": department.id,
            "department_name": department.name,
            "routing_status": IncidentStatus.ASSIGNED.value,
            "message": "Department assigned successfully.",
        }

    @staticmethod
    def manually_assign_department(
        db: Session, incident_id: int, department_id: int, admin_user: User
    ) -> Incident:
        """Manual admin department (re)assignment."""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise EntityNotFoundException("Incident", incident_id)

        department = db.query(Department).filter(Department.id == department_id).first()
        if not department:
            raise EntityNotFoundException("Department", department_id)

        if not department.is_active:
            raise BadRequestException("Cannot assign an inactive department.")

        now = datetime.now(timezone.utc)
        incident.department_id = department.id
        incident.routing_status = IncidentStatus.ASSIGNED.value
        if incident.status in (IncidentStatus.UNASSIGNED.value, IncidentStatus.RISK_ASSESSED.value, IncidentStatus.CREATED.value):
            incident.status = IncidentStatus.ASSIGNED.value
        incident.assigned_at = now
        incident.assigned_by = admin_user.id
        incident.updated_at = now
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def update_incident_status(
        db: Session,
        incident_id: int,
        new_status: str,
        admin_user: User,
        resolution_note: Optional[str] = None,
    ) -> Incident:
        """Update incident status with transition validation."""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise EntityNotFoundException("Incident", incident_id)

        current_status = incident.status
        allowed_transitions = VALID_STATUS_TRANSITIONS.get(current_status, [])

        if new_status != current_status and new_status not in allowed_transitions:
            raise BadRequestException(
                f"Invalid status transition from '{current_status}' to '{new_status}'."
            )

        now = datetime.now(timezone.utc)
        incident.status = new_status
        if new_status in (IncidentStatus.ASSIGNED.value, IncidentStatus.IN_PROGRESS.value, IncidentStatus.RESOLVED.value, IncidentStatus.CLOSED.value):
            incident.routing_status = new_status

        if new_status == IncidentStatus.RESOLVED.value:
            incident.resolved_at = now
            incident.resolved_by = admin_user.id
            if resolution_note:
                incident.resolution_note = resolution_note

        incident.updated_at = now
        db.commit()
        db.refresh(incident)
        return incident
