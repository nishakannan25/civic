from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120, description="Full name of citizen or official")
    email: EmailStr = Field(..., description="Unique email address")
    phone: Optional[str] = Field(None, max_length=30, description="Optional phone number")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100, description="Plain text password (min 6 characters)")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    points: int
    reputation_score: float
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
