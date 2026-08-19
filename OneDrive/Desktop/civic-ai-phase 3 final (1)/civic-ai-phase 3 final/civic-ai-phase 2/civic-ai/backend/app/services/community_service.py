import math
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from ..models.verification import Verification
from ..models.incident import Incident
from ..schemas.verification import VerificationCreate

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two GPS points in meters."""
    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class CommunityService:
    """Service for 500m Community Verification with rating and duplicate protection."""

    MAX_VERIFICATION_RADIUS_METERS = 500.0

    @staticmethod
    def record_verification(
        db: Session,
        user_id: int,
        data: VerificationCreate,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None,
    ) -> Verification:
        incident = db.query(Incident).filter(Incident.id == data.incident_id).first()
        if not incident:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

        # Duplicate verification check
        existing = db.query(Verification).filter(
            Verification.incident_id == data.incident_id,
            Verification.user_id == user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already verified this issue."
            )

        resp_val = data.response.value if hasattr(data.response, "value") else str(data.response)

        # Requirement: YES responses require a rating between 1 and 10
        rating_val = data.rating
        if resp_val == "YES":
            if rating_val is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating from 1 to 10 is required when confirming an issue (YES)."
                )
            if rating_val < 1 or rating_val > 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Rating must be between 1 and 10."
                )
        else:
            # Rating not allowed for NO or UNKNOWN
            rating_val = None

        # Distance calculation and 500m radius check
        dist = data.distance_from_incident
        if dist is None and user_lat is not None and user_lng is not None and incident.latitude is not None and incident.longitude is not None:
            dist = calculate_haversine_distance(user_lat, user_lng, incident.latitude, incident.longitude)

        if dist is not None and dist > CommunityService.MAX_VERIFICATION_RADIUS_METERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Verification failed: You are {int(dist)}m away. Eligible radius is within 500 meters."
            )

        verification = Verification(
            incident_id=data.incident_id,
            user_id=user_id,
            response=resp_val,
            rating=rating_val,
            distance_from_incident=dist,
        )
        db.add(verification)

        # Update incident community count
        if resp_val == "YES":
            incident.community_yes = (incident.community_yes or 0) + 1
        elif resp_val == "NO":
            incident.community_no = (incident.community_no or 0) + 1
        else:
            incident.community_unknown = (incident.community_unknown or 0) + 1

        db.commit()
        db.refresh(verification)
        return verification

    @staticmethod
    def get_nearby_incidents(
        db: Session,
        lat: float,
        lng: float,
        radius_meters: float = 500.0,
        current_user_id: Optional[int] = None,
    ) -> List[dict]:
        """Fetch active incidents within specified radius without exposing private reporter info."""
        incidents = db.query(Incident).filter(Incident.latitude.isnot(None), Incident.longitude.isnot(None)).all()
        result = []
        for inc in incidents:
            d = calculate_haversine_distance(lat, lng, inc.latitude, inc.longitude)
            if d <= radius_meters:
                # Check if current user verified already
                already_verified = False
                if current_user_id:
                    already_verified = any(v.user_id == current_user_id for v in inc.verifications)
                
                result.append({
                    "id": inc.id,
                    "reference_id": f"INC-{inc.id:04d}",
                    "ai_issue_type": inc.ai_issue_type,
                    "description": inc.description if hasattr(inc, "description") else None,
                    "image_url": inc.image_url,
                    "distance_meters": round(d, 1),
                    "created_at": inc.created_at,
                    "status": inc.status,
                    "already_verified": already_verified,
                })
        return result
