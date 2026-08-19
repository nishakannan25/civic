import math
import logging
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def _haversine_distance_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return distance in metres between two GPS coordinates (Haversine formula)."""
    R = 6_371_000  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class NotificationService:
    """In-app notification service — stores records in DB and logs dispatch."""

    @staticmethod
    def send_notification(
        recipient_user_ids: List[int],
        title: str,
        body: str,
        incident_id: Optional[int] = None,
        notification_type: str = "GENERAL",
        db: Optional[Session] = None,
    ) -> bool:
        """Create in-app notification records in the database for all recipients."""
        if not recipient_user_ids:
            return True

        if db is not None:
            try:
                from ..models.notification import Notification
                from datetime import datetime, timezone

                records = [
                    Notification(
                        incident_id=incident_id,
                        recipient_user_id=uid,
                        notification_type=notification_type,
                        status="DELIVERED",
                        created_at=datetime.now(timezone.utc),
                    )
                    for uid in recipient_user_ids
                ]
                db.add_all(records)
                db.commit()
                logger.info(
                    f"[NotificationService] '{title}' dispatched to {len(recipient_user_ids)} users (incident_id={incident_id})."
                )
            except Exception as e:
                logger.warning(f"[NotificationService] DB notification write failed: {e}")
        else:
            logger.info(
                f"[NotificationService] '{title}' (no-db stub) → users {recipient_user_ids}"
            )
        return True

    @staticmethod
    def send_community_verification(
        db: Session,
        incident_id: int,
        incident_lat: float,
        incident_lon: float,
        submitter_user_id: int,
        radius_m: float = 500.0,
        ai_risk_level: Optional[str] = None,
        ai_issue_label: Optional[str] = None,
    ) -> int:
        """
        Find all registered citizens within `radius_m` metres of the incident location
        (excluding the reporter), create COMMUNITY_VERIFICATION notification records,
        and return the count of recipients notified.
        """
        from ..models.user import User

        all_citizens = (
            db.query(User)
            .filter(User.role == "citizen")
            .filter(User.id != submitter_user_id)
            .all()
        )

        # We store latitude / longitude on the User only if they exist.
        # Fall back to notifying all citizens when no geo data is stored on users.
        nearby_ids: List[int] = []
        has_any_geo = any(
            getattr(u, "latitude", None) is not None and getattr(u, "longitude", None) is not None
            for u in all_citizens
        )

        if has_any_geo:
            for u in all_citizens:
                u_lat = getattr(u, "latitude", None)
                u_lon = getattr(u, "longitude", None)
                if u_lat is not None and u_lon is not None:
                    dist = _haversine_distance_m(incident_lat, incident_lon, u_lat, u_lon)
                    if dist <= radius_m:
                        nearby_ids.append(u.id)
        else:
            # No geo data on users — notify all citizens as a broadcast
            nearby_ids = [u.id for u in all_citizens]

        if not nearby_ids:
            logger.info(f"[CommunityVerification] No nearby citizens found within {radius_m}m of incident {incident_id}.")
            return 0

        risk_str = ai_risk_level or "UNKNOWN"
        issue_str = ai_issue_label or "Civic Issue"
        title = f"🚨 Community Alert — {risk_str} Risk {issue_str}"
        body = (
            f"A new civic incident has been reported near your location. "
            f"Incident #{incident_id} | AI Risk Level: {risk_str}. "
            f"Please verify if this issue exists in your area."
        )

        NotificationService.send_notification(
            recipient_user_ids=nearby_ids,
            title=title,
            body=body,
            incident_id=incident_id,
            notification_type="COMMUNITY_VERIFICATION",
            db=db,
        )

        logger.info(
            f"[CommunityVerification] Sent to {len(nearby_ids)} citizens within {radius_m}m of incident {incident_id}."
        )
        return len(nearby_ids)
