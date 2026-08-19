from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

class DepartmentBase(BaseModel):
    name: str
    description: Optional[str] = None
    issue_types: str
    service_area: Optional[str] = None
    contact_information: Optional[str] = None
    is_active: bool = True

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    issue_types: Optional[str] = None
    service_area: Optional[str] = None
    contact_information: Optional[str] = None
    is_active: Optional[bool] = None

class DepartmentResponse(DepartmentBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
