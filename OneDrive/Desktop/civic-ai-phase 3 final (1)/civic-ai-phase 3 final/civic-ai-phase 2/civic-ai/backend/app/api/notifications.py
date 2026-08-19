from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..models.user import User
from ..core.security import get_current_user
from ..schemas.common import MessageResponse

router = APIRouter(prefix="/notifications", tags=["Notifications (Phase 8 Blueprint)"])

@router.get("", response_model=MessageResponse, status_code=status.HTTP_200_OK)
def list_user_notifications(current_user: User = Depends(get_current_user)):
    return MessageResponse(
        message="Notifications API blueprint ready.",
        detail="Full push notification delivery will be enabled in Phase 8.",
    )
