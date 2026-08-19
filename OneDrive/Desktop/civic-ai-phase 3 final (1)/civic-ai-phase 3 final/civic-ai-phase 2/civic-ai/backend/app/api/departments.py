from typing import List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database.connection import get_db
from ..models.department import Department
from ..schemas.common import MessageResponse

router = APIRouter(prefix="/departments", tags=["Municipal Departments (Phase 11 Blueprint)"])

class DepartmentResponse(BaseModel):
    id: int
    name: str
    issue_types: str
    service_area: str | None = None
    contact_information: str | None = None

    class Config:
        from_attributes = True

@router.get("", response_model=List[DepartmentResponse], status_code=status.HTTP_200_OK)
def list_departments(db: Session = Depends(get_db)):
    departments = db.query(Department).all()
    return [DepartmentResponse.model_validate(dept) for dept in departments]
