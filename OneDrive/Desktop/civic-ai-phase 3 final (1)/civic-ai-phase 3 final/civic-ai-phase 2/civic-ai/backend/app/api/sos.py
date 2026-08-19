from typing import Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..models.user import User
from ..services.sos_service import SOSService
from ..core.security import get_current_user

router = APIRouter(prefix="/sos", tags=["Emergency SOS (Phase 10 Blueprint)"])

class SOSTriggerRequest(BaseModel):
    incident_id: Optional[int] = None
    reason: str = Field("Manual SOS Trigger", description="Reason for triggering emergency")

class SOSTriggerResponse(BaseModel):
    id: int
    status: str
    trigger_reason: Optional[str]
    risk_score: Optional[float]
    message: str

@router.post(
    "/trigger",
    response_model=SOSTriggerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger emergency SOS dispatch",
)
def trigger_sos(
    sos_in: SOSTriggerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sos_event = SOSService.trigger_emergency_event(
        db,
        incident_id=sos_in.incident_id,
        trigger_reason=sos_in.reason,
    )
    return SOSTriggerResponse(
        id=sos_event.id,
        status=sos_event.status,
        trigger_reason=sos_event.trigger_reason,
        risk_score=sos_event.risk_score,
        message="Emergency SOS event logged successfully (Phase 1 blueprint).",
    )
