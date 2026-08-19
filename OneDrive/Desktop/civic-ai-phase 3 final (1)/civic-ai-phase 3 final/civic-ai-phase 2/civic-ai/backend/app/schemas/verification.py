from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator
from ..core.constants import VerificationResponse as VerificationEnum

class VerificationCreate(BaseModel):
    incident_id: int = Field(..., description="ID of incident being verified")
    response: VerificationEnum = Field(..., description="Response: YES, NO, or UNKNOWN")
    rating: Optional[int] = Field(None, description="Severity rating 1 to 10 for YES verification")
    distance_from_incident: Optional[float] = Field(None, ge=0.0, description="Citizen distance in meters")

    @field_validator("rating")
    @classmethod
    def validate_rating(cls, v, info):
        if v is not None:
            if v < 1 or v > 10:
                raise ValueError("Rating must be between 1 and 10")
        return v

class VerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    user_id: int
    response: str
    rating: Optional[int] = None
    distance_from_incident: Optional[float] = None
    created_at: datetime

