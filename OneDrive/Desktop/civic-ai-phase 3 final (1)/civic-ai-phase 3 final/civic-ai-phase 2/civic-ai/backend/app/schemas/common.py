from typing import Optional, Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")

class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "civic-ai-backend"

class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None

class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    skip: int = 0
    limit: int = 50
    items: List[T]
