from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..models.user import User
from ..schemas.verification import VerificationCreate, VerificationResponse
from ..services.community_service import CommunityService
from ..core.security import get_current_user

router = APIRouter(prefix="/community", tags=["Community Verification (Phase 7 & 10A)"])

@router.post(
    "/verify",
    response_model=VerificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit community verification for an incident",
)
def submit_verification(
    verification_in: VerificationCreate,
    user_lat: Optional[float] = Query(None, description="Current citizen latitude for 500m check"),
    user_lng: Optional[float] = Query(None, description="Current citizen longitude for 500m check"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record citizen verification for a reported civic issue."""
    verification = CommunityService.record_verification(
        db,
        user_id=current_user.id,
        data=verification_in,
        user_lat=user_lat,
        user_lng=user_lng,
    )
    return VerificationResponse.model_validate(verification)

@router.post(
    "/incidents/{incident_id}/verify",
    response_model=VerificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit community verification for specific incident ID",
)
def submit_verification_for_incident(
    incident_id: int,
    verification_in: VerificationCreate,
    user_lat: Optional[float] = Query(None),
    user_lng: Optional[float] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Record verification for a specific incident path parameter."""
    verification_in.incident_id = incident_id
    verification = CommunityService.record_verification(
        db,
        user_id=current_user.id,
        data=verification_in,
        user_lat=user_lat,
        user_lng=user_lng,
    )
    return VerificationResponse.model_validate(verification)

@router.get(
    "/incidents/nearby",
    summary="Get nearby incidents within 500 meters for community verification",
)
def get_nearby_incidents(
    lat: float = Query(..., description="Citizen latitude"),
    lng: float = Query(..., description="Citizen longitude"),
    radius: float = Query(500.0, description="Verification radius in meters (default 500m)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get active incidents within 500 meters of citizen location for community verification."""
    return CommunityService.get_nearby_incidents(
        db,
        lat=lat,
        lng=lng,
        radius_meters=radius,
        current_user_id=current_user.id,
    )
