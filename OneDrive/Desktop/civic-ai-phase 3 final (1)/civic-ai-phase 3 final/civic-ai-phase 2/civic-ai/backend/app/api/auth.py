from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from ..core.security import get_password_hash, verify_password, create_access_token
from ..core.exceptions import DuplicateEmailException, InvalidCredentialsException

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new citizen or user account",
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if email is already registered
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise DuplicateEmailException(user_in.email)

    # Hash the password and persist user
    hashed_password = get_password_hash(user_in.password)
    user = User(
        name=user_in.name,
        email=user_in.email,
        phone=user_in.phone,
        password_hash=hashed_password,
        role="citizen",
        points=0,
        reputation_score=5.0,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate JWT access token
    access_token = create_access_token(subject=user.id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )

from fastapi import Request

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user and return JWT access token",
)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    email = None
    password = None

    # Check content type to parse JSON or Form data
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")
    else:
        form = await request.form()
        email = form.get("email") or form.get("username")
        password = form.get("password")

    if not email or not password:
        raise InvalidCredentialsException()

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise InvalidCredentialsException()

    access_token = create_access_token(subject=user.id)
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )

