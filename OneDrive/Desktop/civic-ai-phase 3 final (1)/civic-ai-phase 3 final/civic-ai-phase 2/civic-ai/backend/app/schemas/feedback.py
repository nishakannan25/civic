from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

class FeedbackCreate(BaseModel):
    satisfied: str = Field(..., description="YES or NO satisfaction response")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Optional satisfaction rating from 1 to 5")
    feedback_text: Optional[str] = Field(None, max_length=1000, description="Optional feedback text")

    @field_validator("satisfied")
    @classmethod
    def validate_satisfied(cls, v):
        upper = v.upper()
        if upper not in ["YES", "NO"]:
            raise ValueError("satisfied must be 'YES' or 'NO'")
        return upper

class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    user_id: int
    satisfied: str
    rating: Optional[int] = None
    feedback_text: Optional[str] = None
    created_at: datetime
