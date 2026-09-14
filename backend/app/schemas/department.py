from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models import UserStatus


class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)
    description: Optional[str] = None
    head_id: Optional[int] = None


class DepartmentCreate(DepartmentBase):
    @field_validator("code")
    @classmethod
    def code_upper(cls, v):
        return v.upper().strip()


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    description: Optional[str] = None
    head_id: Optional[int] = None
    status: Optional[UserStatus] = None

    @field_validator("code")
    @classmethod
    def code_upper(cls, v):
        if v:
            return v.upper().strip()
        return v


class DepartmentResponse(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    head: Optional["EmployeeListResponse"] = None
    student_count: int = 0
    employee_count: int = 0


class DepartmentFilter(BaseModel):
    search: Optional[str] = None
    status: Optional[UserStatus] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"


from app.schemas.employee import EmployeeListResponse