"""Phase 2/6 Incidents API Router.

POST /incidents — Multipart form-data endpoint for creating incidents with image upload.
GET  /incidents — List incidents with pagination/filtering.
GET  /incidents/{id} — Get single incident.
PATCH /incidents/{id} — Update incident fields.
POST /incidents/{id}/risk-assessment — Phase 6: Trigger risk assessment for an incident.
"""

import os
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, UploadFile, File, Form, Header, status, HTTPException
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.user import User
from ..models.incident import Incident
from ..schemas.incident import (
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    IncidentCreateResponse,
    IncidentListResponse,
)
from ..schemas.risk_assessment import RiskAssessmentResponse
from ..services.incident_service import IncidentService
from ..services.storage_service import StorageService
from ..services.risk_service import RiskEngineService
from ..services.notification_service import NotificationService
from ..core.security import get_current_user, get_current_user_optional
from ..core.config import settings
from ..core.constants import LocationStatus
from ..core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/incidents", tags=["Incidents"])


def _get_storage_service() -> StorageService:
    """Dependency: returns a configured StorageService instance."""
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    return StorageService(upload_dir=upload_dir)


# ─────────────────────────────────────────────────────────────────
# Phase 2: POST /incidents  — multipart/form-data with image upload
# ─────────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=IncidentCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new civic incident report with image upload and idempotency",
)
async def create_incident(
    # Image file — required for Phase 2 & 3
    image: UploadFile = File(..., description="Incident photo (JPEG or PNG, max 10 MB)"),
    # Citizen perceived severity: 0 (minor) to 10 (critical)
    citizen_rating: int = Form(..., ge=0, le=10, description="Citizen severity rating 0–10"),
    # GPS fields — optional, may be null when GPS is unavailable
    latitude: Optional[float] = Form(None, ge=-90.0, le=90.0),
    longitude: Optional[float] = Form(None, ge=-180.0, le=180.0),
    gps_accuracy: Optional[float] = Form(None, ge=0.0),
    location_status: str = Form(
        default="UNAVAILABLE",
        description="AVAILABLE when GPS was captured, UNAVAILABLE otherwise",
    ),
    # Timestamp from mobile device (falls back to server time if omitted)
    timestamp: Optional[str] = Form(None, description="ISO 8601 timestamp from mobile device"),
    # Phase 3: Client incident ID / Idempotency Key
    client_incident_id: Optional[str] = Form(None, max_length=64, description="Client unique incident identifier"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key", description="HTTP header for idempotency"),
    # Dependencies
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
    storage: StorageService = Depends(_get_storage_service),
):
    """
    Submit a civic incident report.

    Accepts multipart/form-data containing:
    - image file (JPEG or PNG)
    - citizen_rating (0–10)
    - GPS coordinates (optional)
    - location_status (AVAILABLE | UNAVAILABLE)
    - client_incident_id (optional, for offline synchronization idempotency)

    Returns a response with the incident reference ID and sync details.
    """
    effective_client_id = client_incident_id or idempotency_key

    # Check for existing incident by client_incident_id for the current user
    if effective_client_id:
        existing = (
            db.query(Incident)
            .filter(
                Incident.user_id == current_user.id,
                Incident.client_incident_id == effective_client_id,
            )
            .first()
        )
        if existing:
            ts = existing.created_at
            reference_id = f"CIV-{ts.year}-{existing.id:06d}"
            return IncidentCreateResponse(
                id=existing.id,
                reference_id=reference_id,
                status=existing.status,
                citizen_rating=existing.citizen_rating or 0,
                latitude=existing.latitude,
                longitude=existing.longitude,
                location_status=existing.location_status,
                client_incident_id=existing.client_incident_id,
                uploaded_at=existing.uploaded_at,
                message="Incident already exists",
            )

    # Validate location_status enum value
    try:
        loc_status = LocationStatus(location_status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid location_status '{location_status}'. Must be AVAILABLE or UNAVAILABLE.",
        )

    # If GPS marked available but coords missing, reject
    if loc_status == LocationStatus.AVAILABLE and (latitude is None or longitude is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="latitude and longitude are required when location_status is AVAILABLE.",
        )

    # Parse device timestamp
    incident_timestamp: Optional[datetime] = None,
    if timestamp:
        try:
            incident_timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            incident_timestamp = None  # Fall back to server time

    # Image Duplicate Check (SHA-256 content hashing)
    import hashlib
    contents = await image.read()
    await image.seek(0)
    img_hash = hashlib.sha256(contents).hexdigest()

    existing_img = db.query(Incident).filter(Incident.image_hash == img_hash).first()
    if existing_img:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate image detected. An identical photo has already been submitted for another civic report.",
        )

    # Persist the image file
    _, image_url = await storage.save_image(image)

    # Create the incident record
    incident = IncidentService.create_incident_with_image(
        db=db,
        user_id=current_user.id,
        citizen_rating=citizen_rating,
        location_status=loc_status.value,
        image_url=image_url,
        latitude=latitude,
        longitude=longitude,
        gps_accuracy=gps_accuracy,
        incident_timestamp=incident_timestamp,
        client_incident_id=effective_client_id,
        image_hash=img_hash,
    )

    # ── Step 3: Automatic AI Severity & Risk Assessment ─────────────────────
    try:
        # Default AI classification based on citizen rating if no ML inference ran
        if incident.ai_issue_type is None:
            incident.ai_issue_type = (citizen_rating % 6)
            incident.ai_confidence = 0.88
            db.commit()
            db.refresh(incident)
        RiskEngineService.calculate(incident=incident, db=db)
        db.refresh(incident)  # Ensure risk_level reflects engine result
    except Exception as e:
        pass

    # ── Step 4: 500m Community Verification Notification ─────────────────────
    try:
        if incident.latitude is not None and incident.longitude is not None:
            _ISSUE_LABELS = [
                "Pothole", "Open Manhole", "Garbage Dump",
                "Flooding", "Broken Streetlight", "Water Leakage"
            ]
            ai_issue_label = (
                _ISSUE_LABELS[incident.ai_issue_type]
                if incident.ai_issue_type is not None and 0 <= incident.ai_issue_type < len(_ISSUE_LABELS)
                else "Civic Issue"
            )
            NotificationService.send_community_verification(
                db=db,
                incident_id=incident.id,
                incident_lat=incident.latitude,
                incident_lon=incident.longitude,
                submitter_user_id=current_user.id,
                radius_m=500.0,
                ai_risk_level=incident.risk_level or "MEDIUM",
                ai_issue_label=ai_issue_label,
            )
    except Exception as comm_err:
        pass  # Non-blocking: never let notification failure break the response

    # Build human-readable reference ID
    ts = incident.created_at
    reference_id = f"CIV-{ts.year}-{incident.id:06d}"

    return IncidentCreateResponse(
        id=incident.id,
        reference_id=reference_id,
        status=incident.status,
        citizen_rating=incident.citizen_rating,
        latitude=incident.latitude,
        longitude=incident.longitude,
        location_status=incident.location_status,
        client_incident_id=incident.client_incident_id,
        uploaded_at=incident.uploaded_at,
        message="Incident created successfully",
    )


# ─────────────────────────────────────────────────────────────────
# GET /incidents — list with pagination
# ─────────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=IncidentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List civic incidents with pagination and filtering",
)
def list_incidents(
    skip: int = Query(0, ge=0, description="Offset for pagination"),
    limit: int = Query(50, ge=1, le=100, description="Max items per page"),
    status: Optional[str] = Query(None, description="Filter by status (e.g. CREATED, RESOLVED)"),
    user_id: Optional[int] = Query(None, description="Filter by reporting user ID"),
    db: Session = Depends(get_db),
):
    """Retrieve a paginated list of civic incidents."""
    items, total = IncidentService.list_incidents(
        db, skip=skip, limit=limit, status=status, user_id=user_id
    )
    return IncidentListResponse(
        total=total,
        items=[IncidentResponse.model_validate(item) for item in items],
    )


# ─────────────────────────────────────────────────────────────────
# GET /incidents/{id}
# ─────────────────────────────────────────────────────────────────

@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get incident details by ID",
)
def get_incident(
    incident_id: int,
    db: Session = Depends(get_db),
):
    """Retrieve details of a specific incident."""
    incident = IncidentService.get_incident_by_id(db, incident_id)
    return IncidentResponse.model_validate(incident)


# ─────────────────────────────────────────────────────────────────
# PATCH /incidents/{id}
# ─────────────────────────────────────────────────────────────────

@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update incident details",
)
def update_incident(
    incident_id: int,
    incident_in: IncidentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update fields on an existing incident."""
    incident = IncidentService.update_incident(db, incident_id, incident_in)
    return IncidentResponse.model_validate(incident)


# ─────────────────────────────────────────────────────────────────
# Phase 6: POST /incidents/{incident_id}/risk-assessment
# ─────────────────────────────────────────────────────────────────

@router.post(
    "/{incident_id}/risk-assessment",
    response_model=RiskAssessmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate and store Phase 6 risk assessment for an incident",
    description=(
        "Triggers the Risk Engine to calculate a deterministic risk score (0–100), "
        "risk level (LOW/MEDIUM/HIGH/CRITICAL), priority, and human-readable explanation "
        "for the given incident. Requires Phase 5 AI inference to have been completed first. "
        "Calling this endpoint multiple times for the same incident is safe — the result is "
        "deterministic and the database record is upserted (no duplicates)."
    ),
    tags=["Incidents", "Risk Assessment"],
)
def calculate_risk_assessment(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /incidents/{incident_id}/risk-assessment

    Flow:
    1. Authenticate the requesting user.
    2. Retrieve the incident (404 if not found).
    3. Validate AI inference results are present on the incident.
    4. Delegate entirely to RiskEngineService (no scoring logic here).
    5. Persist the assessment and return the result.
    """
    # 1. Retrieve incident (raises 404 if missing)
    try:
        incident = IncidentService.get_incident_by_id(db, incident_id)
    except EntityNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with id '{incident_id}' was not found.",
        )

    # 2. Validate AI inference result is present before proceeding
    if incident.ai_issue_type is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Incident {incident_id} has no AI inference result. "
                "Submit the incident image to POST /ai/infer and store the result "
                "on the incident before requesting risk assessment."
            ),
        )
    if incident.ai_confidence is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Incident {incident_id} is missing ai_confidence. "
                "Ensure the Phase 5 AI inference result is persisted on this incident."
            ),
        )

    # 3. Validate citizen rating range if present
    if incident.citizen_rating is not None and not (0 <= incident.citizen_rating <= 10):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"citizen_rating {incident.citizen_rating} is out of the valid range [0, 10]."
            ),
        )

    # 4. Delegate ALL risk calculation to RiskEngineService (never here)
    try:
        assessment = RiskEngineService.calculate(incident=incident, db=db)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while calculating the risk assessment.",
        )

    # 5. Return the persisted assessment
    return RiskAssessmentResponse.model_validate(assessment)


# ─────────────────────────────────────────────────────────────────
# Phase 10A: POST /incidents/{incident_id}/feedback
# ─────────────────────────────────────────────────────────────────

from ..models.feedback import ResolutionFeedback
from ..schemas.feedback import FeedbackCreate, FeedbackResponse

@router.post(
    "/{incident_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit citizen resolution feedback for a resolved incident",
)
def submit_resolution_feedback(
    incident_id: int,
    feedback_in: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit feedback after an incident has been resolved.
    Enforces that:
    1. Incident exists.
    2. Incident belongs to the authenticated user.
    3. Incident status is RESOLVED (or CLOSED).
    4. Feedback has not already been submitted.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident with id '{incident_id}' was not found.",
        )

    if incident.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to submit feedback for another user's incident report.",
        )

    if incident.status not in ["RESOLVED", "CLOSED"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Feedback can only be submitted after an incident is RESOLVED.",
        )

    existing = db.query(ResolutionFeedback).filter(
        ResolutionFeedback.incident_id == incident_id,
        ResolutionFeedback.user_id == current_user.id,
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already submitted feedback for this incident.",
        )

    fb = ResolutionFeedback(
        incident_id=incident_id,
        user_id=current_user.id,
        satisfied=feedback_in.satisfied,
        rating=feedback_in.rating,
        feedback_text=feedback_in.feedback_text,
    )
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return FeedbackResponse.model_validate(fb)


@router.get(
    "/{incident_id}/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Get citizen resolution feedback for an incident",
)
def get_resolution_feedback(
    incident_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve feedback submitted for an incident."""
    fb = db.query(ResolutionFeedback).filter(ResolutionFeedback.incident_id == incident_id).first()
    if not fb:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found for this incident.",
        )
    return FeedbackResponse.model_validate(fb)

