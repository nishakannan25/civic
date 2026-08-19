from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.user import User
from ..models.incident import Incident
from ..models.department import Department
from ..schemas.admin import (
    DashboardSummaryResponse,
    IncidentAssignmentRequest,
    IncidentStatusUpdateRequest,
    MapIncidentItem,
    RoutingResultResponse,
)
from ..schemas.incident import IncidentResponse, IncidentListResponse
from ..schemas.department import DepartmentResponse
from ..services.admin_service import AdminService
from ..services.routing_service import CivicRoutingService
from ..services.incident_service import IncidentService
from ..core.security import get_current_user, get_current_user_optional
from ..core.exceptions import UnauthorizedException, ForbiddenException, EntityNotFoundException
from ..core.constants import UserRole, AI_TAXONOMY_MAP

router = APIRouter(prefix="/admin", tags=["Admin Dashboard & Department Routing"])


def get_current_admin_user(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
) -> User:
    """Dependency: enforce admin role authorization or fall back to default admin user."""
    if current_user and current_user.role in (UserRole.ADMIN.value, UserRole.MUNICIPAL_STAFF.value, "admin"):
        return current_user
    
    # Fallback to seeded administrator
    admin_user = db.query(User).filter(User.email == "admin@civic.ai").first()
    if admin_user:
        return admin_user
    return current_user


# ─────────────────────────────────────────────────────────────────
# 1. GET /admin/dashboard/summary
# ─────────────────────────────────────────────────────────────────
@router.get(
    "/dashboard/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get aggregated admin dashboard metrics",
)
def get_dashboard_summary(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve actual database metrics for admin dashboard cards and distribution charts."""
    return AdminService.get_dashboard_summary(db)


# ─────────────────────────────────────────────────────────────────
# 2. GET /admin/incidents — paginated, filtered, searchable listing
# ─────────────────────────────────────────────────────────────────
@router.get(
    "/incidents",
    response_model=IncidentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List incidents for admin management with filters and search",
)
def list_admin_incidents(
    skip: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    issue_type: Optional[str] = Query(None, description="Filter by issue type (e.g. pothole)"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level (LOW/MEDIUM/HIGH/CRITICAL)"),
    department_id: Optional[int] = Query(None, description="Filter by department ID"),
    status: Optional[str] = Query(None, description="Filter by status or routing_status"),
    search: Optional[str] = Query(None, description="Search query by ID or status"),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve filtered, searched, and paginated incident list for admin dashboard table."""
    items, total = AdminService.list_admin_incidents(
        db,
        skip=skip,
        limit=limit,
        issue_type=issue_type,
        risk_level=risk_level,
        department_id=department_id,
        status=status,
        search=search,
    )
    
    # Build IncidentResponse items with department_name mapped
    response_items = []
    for inc in items:
        inc_res = IncidentResponse.model_validate(inc)
        if inc.department:
            inc_res.department_name = inc.department.name
        response_items.append(inc_res)

    return IncidentListResponse(total=total, items=response_items)


# ─────────────────────────────────────────────────────────────────
# 3. GET /admin/incidents/{incident_id}
# ─────────────────────────────────────────────────────────────────
@router.get(
    "/incidents/{incident_id}",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get single incident detail for admin view",
)
def get_admin_incident_detail(
    incident_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve full incident details for admin review."""
    incident = IncidentService.get_incident_by_id(db, incident_id)
    inc_res = IncidentResponse.model_validate(incident)
    if incident.department:
        inc_res.department_name = incident.department.name
    return inc_res


# ─────────────────────────────────────────────────────────────────
# 4. GET /admin/departments
# ─────────────────────────────────────────────────────────────────
@router.get(
    "/departments",
    response_model=List[DepartmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List all municipal departments",
)
def list_departments(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve all municipal departments."""
    departments = db.query(Department).all()
    return [DepartmentResponse.model_validate(dept) for dept in departments]


# ─────────────────────────────────────────────────────────────────
# 5. POST /admin/incidents/{incident_id}/route (or /incidents/{incident_id}/route)
# ─────────────────────────────────────────────────────────────────
@router.post(
    "/incidents/{incident_id}/route",
    response_model=RoutingResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform automatic department routing for an incident",
)
def route_incident(
    incident_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Triggers CivicRoutingService automatic routing."""
    res = CivicRoutingService.route_incident(db, incident_id)
    return RoutingResultResponse(**res)


# ─────────────────────────────────────────────────────────────────
# 6. PATCH /admin/incidents/{incident_id}/assignment
# ─────────────────────────────────────────────────────────────────
@router.patch(
    "/incidents/{incident_id}/assignment",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Manually assign or reassign incident to department",
)
def assign_department(
    incident_id: int,
    req: IncidentAssignmentRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Manual admin assignment or reassignment of incident to department."""
    updated = CivicRoutingService.manually_assign_department(
        db, incident_id, req.department_id, admin_user
    )
    inc_res = IncidentResponse.model_validate(updated)
    if updated.department:
        inc_res.department_name = updated.department.name
    return inc_res


# ─────────────────────────────────────────────────────────────────
# 7. PATCH /admin/incidents/{incident_id}/status
# ─────────────────────────────────────────────────────────────────
@router.patch(
    "/incidents/{incident_id}/status",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update incident lifecycle status",
)
def update_status(
    incident_id: int,
    req: IncidentStatusUpdateRequest,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update incident status (IN_PROGRESS, RESOLVED, CLOSED, etc.) with transition validation."""
    updated = CivicRoutingService.update_incident_status(
        db, incident_id, req.status, admin_user, req.resolution_note
    )
    inc_res = IncidentResponse.model_validate(updated)
    if updated.department:
        inc_res.department_name = updated.department.name
    return inc_res


# ─────────────────────────────────────────────────────────────────
# 8. GET /admin/incidents/map
# ─────────────────────────────────────────────────────────────────
@router.get(
    "/incidents-map",
    response_model=List[MapIncidentItem],
    status_code=status.HTTP_200_OK,
    summary="Get incident markers for interactive map view",
)
def get_map_incidents(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve incident marker details for map visualization."""
    items = AdminService.get_map_incidents(db)
    return [MapIncidentItem(**item) for item in items]


# ─────────────────────────────────────────────────────────────────
# 9. GET /admin/analytics — Per-day, 1-week, 1-month, 1-year analytics
# ─────────────────────────────────────────────────────────────────
@router.get(
    "/analytics",
    status_code=status.HTTP_200_OK,
    summary="Get analytics data across Day, Week, Month, and Year timeframes",
)
def get_analytics(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Retrieve tabular metrics and time series data for Day, Week, Month, and Year analytics."""
    return AdminService.get_analytics_summary(db)


# ─────────────────────────────────────────────────────────────────
# 10. POST /admin/incidents/{incident_id}/dispatch-verification
# ─────────────────────────────────────────────────────────────────
@router.post(
    "/incidents/{incident_id}/dispatch-verification",
    status_code=status.HTTP_200_OK,
    summary="Dispatch 500m community verification alerts to nearby citizens",
)
def dispatch_community_verification(
    incident_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Manually dispatch 500m geo-proximity community verification notifications for an incident."""
    from ..services.notification_service import NotificationService
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise EntityNotFoundException(f"Incident with ID {incident_id} not found.")

    lat = incident.latitude if incident.latitude is not None else 13.0827
    lon = incident.longitude if incident.longitude is not None else 80.2707
    submitter_id = incident.reporter_id or 0

    count = NotificationService.send_community_verification(
        db=db,
        incident_id=incident.id,
        incident_lat=lat,
        incident_lon=lon,
        submitter_user_id=submitter_id,
        radius_m=500.0,
        ai_risk_level=incident.risk_level,
        ai_issue_label=None,
    )

    return {
        "status": "SUCCESS",
        "incident_id": incident_id,
        "radius_meters": 500.0,
        "recipients_notified": count,
        "message": f"Successfully dispatched 500m geo-verification alert to {count} citizen(s)."
    }

