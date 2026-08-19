from typing import Dict, Optional
from pydantic import BaseModel, Field


class InferenceResponse(BaseModel):
    predicted_class: str = Field(
        ...,
        description="Predicted crisis display name or 'LOW_CONFIDENCE'",
        example="Pothole / Road Damage"
    )
    confidence: float = Field(
        ...,
        description="Maximum model prediction confidence probability (0.0 to 1.0)",
        example=0.9421
    )
    model_version: str = Field(
        ...,
        description="Version string of the loaded Phase 4 model artifact",
        example="phase4-v1"
    )
    inference_time_ms: float = Field(
        ...,
        description="Time taken to process the image and execute inference in milliseconds",
        example=45.2
    )
    probabilities: Dict[str, float] = Field(
        ...,
        description="Mapping of all 6 crisis display names to their output softmax probabilities"
    )


class AIHealthResponse(BaseModel):
    status: str = Field(..., description="'ready' when model is loaded, 'unavailable' otherwise", example="ready")
    model_version: str = Field(..., description="Loaded model version string", example="phase4-v1")
    model_loaded: bool = Field(..., description="True if model weights are loaded in memory", example=True)
