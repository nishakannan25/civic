"""Phase 2 Incident Service.

Handles business logic for incident creation, retrieval, and updates.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.incident import Incident
from ..schemas.incident import IncidentCreate, IncidentUpdate
from ..core.constants import IncidentStatus, LocationStatus
from ..core.exceptions import EntityNotFoundException


class IncidentService:

    @staticmethod
    def create_incident(db: Session, user_id: int, data: IncidentCreate) -> Incident:
        """
        Create a new incident from JSON body (legacy / test path).
        Used by tests and direct API calls without image upload.
        """
        if data.client_incident_id:
            existing = (
                db.query(Incident)
                .filter(
                    Incident.user_id == user_id,
                    Incident.client_incident_id == data.client_incident_id,
                )
                .first()
            )
            if existing:
                return existing

        now = datetime.now(timezone.utc)
        incident = Incident(
            user_id=user_id,
            latitude=data.latitude,
            longitude=data.longitude,
            gps_accuracy=data.gps_accuracy,
            location_status=data.location_status or LocationStatus.UNAVAILABLE.value,
            image_url=data.image_url,
            citizen_rating=data.citizen_rating,
            status=IncidentStatus.CREATED.value,
            community_yes=0,
            community_no=0,
            community_unknown=0,
            client_incident_id=data.client_incident_id,
            uploaded_at=now,
            created_at=now,
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def create_incident_with_image(
        db: Session,
        user_id: int,
        citizen_rating: int,
        location_status: str,
        image_url: Optional[str] = None,
        description: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        gps_accuracy: Optional[float] = None,
        incident_timestamp: Optional[datetime] = None,
        client_incident_id: Optional[str] = None,
        image_hash: Optional[str] = None,
    ) -> Incident:
        """
        Phase 3: Create an incident from multipart form data with image upload and idempotency.
        """
        # Idempotency check: prevent duplicate submissions for same user and client_incident_id
        if client_incident_id:
            existing = (
                db.query(Incident)
                .filter(
                    Incident.user_id == user_id,
                    Incident.client_incident_id == client_incident_id,
                )
                .first()
            )
            if existing:
                return existing

        # Validate: if GPS is marked available, coordinates must be present
        if location_status == LocationStatus.AVAILABLE.value:
            if latitude is None or longitude is None:
                raise ValueError(
                    "Latitude and longitude are required when location_status is AVAILABLE."
                )

        # Validate coordinate ranges when provided
        if latitude is not None and not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude must be between -90 and 90.")
        if longitude is not None and not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude must be between -180 and 180.")

        # Validate citizen_rating range
        if not (0 <= citizen_rating <= 10):
            raise ValueError("citizen_rating must be between 0 and 10.")

        now = datetime.now(timezone.utc)
        incident = Incident(
            user_id=user_id,
            description=description,
            image_url=image_url,
            latitude=latitude,
            longitude=longitude,
            gps_accuracy=gps_accuracy,
            location_status=location_status,
            timestamp=incident_timestamp or now,
            citizen_rating=citizen_rating,
            status=IncidentStatus.CREATED.value,
            community_yes=0,
            community_no=0,
            community_unknown=0,
            client_incident_id=client_incident_id,
            image_hash=image_hash,
            uploaded_at=now,
            created_at=now,
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def get_incident_by_id(db: Session, incident_id: int) -> Incident:
        """Retrieve a single incident by ID."""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if not incident:
            raise EntityNotFoundException("Incident", incident_id)
        return incident

    @staticmethod
    def list_incidents(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        status: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Tuple[List[Incident], int]:
        """List incidents with optional filtering and pagination."""
        query = db.query(Incident)
        if status:
            query = query.filter(Incident.status == status)
        if user_id:
            query = query.filter(Incident.user_id == user_id)

        total = query.count()
        items = query.order_by(desc(Incident.created_at)).offset(skip).limit(limit).all()
        return items, total

    @staticmethod
    def update_incident(db: Session, incident_id: int, data: IncidentUpdate) -> Incident:
        """Update an existing incident record."""
        incident = IncidentService.get_incident_by_id(db, incident_id)

        if data.status is not None:
            incident.status = data.status.value
        if data.citizen_rating is not None:
            incident.citizen_rating = data.citizen_rating
        if data.image_url is not None:
            incident.image_url = data.image_url

        incident.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(incident)
        return incident
