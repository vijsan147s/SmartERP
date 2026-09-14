from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from app.models import UserStatus


class EmployeeBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    department_id: Optional[int] = None
    designation: str = Field(..., min_length=1, max_length=100)
    joining_date: date
    salary: Decimal = Field(..., ge=0)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=255)
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("employee_id")
    @classmethod
    def employee_id_format(cls, v):
        return v.upper().strip()

    @field_validator("username")
    @classmethod
    def username_lower(cls, v):
        return v.lower().strip()


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    department_id: Optional[int] = None
    designation: Optional[str] = Field(None, min_length=1, max_length=100)
    salary: Optional[Decimal] = Field(None, ge=0)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=255)
    status: Optional[UserStatus] = None


class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: str
    user_id: int
    email: str = ""
    username: str = ""
    full_name: str = ""
    phone: Optional[str] = None
    department_id: Optional[int] = None
    designation: str
    joining_date: date
    salary: Decimal
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    department: Optional["DepartmentResponse"] = None


class EmployeeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: str
    full_name: str
    email: str
    phone: Optional[str]
    department_name: Optional[str] = None
    designation: str
    joining_date: date
    salary: Decimal
    status: UserStatus
    created_at: datetime


class EmployeeFilter(BaseModel):
    search: Optional[str] = None
    department_id: Optional[int] = None
    designation: Optional[str] = None
    status: Optional[UserStatus] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"


from app.schemas.department import DepartmentResponse