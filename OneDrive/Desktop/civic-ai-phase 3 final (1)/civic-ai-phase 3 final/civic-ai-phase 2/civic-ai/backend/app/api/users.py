from fastapi import APIRouter, Depends, status
from ..models.user import User
from ..schemas.user import UserResponse
from ..core.security import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get currently authenticated citizen profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    """Return profile details for the authenticated user (excludes password hash)."""
    return UserResponse.model_validate(current_user)
