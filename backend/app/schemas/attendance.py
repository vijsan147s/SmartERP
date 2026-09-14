from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models import AttendanceStatus


class AttendanceBase(BaseModel):
    date: date
    status: AttendanceStatus
    remarks: Optional[str] = None


class AttendanceCreate(AttendanceBase):
    student_id: Optional[int] = None
    employee_id: Optional[int] = None

    @field_validator("student_id", "employee_id", mode="before")
    @classmethod
    def validate_one_entity(cls, v, info):
        return v


class AttendanceBulkCreate(BaseModel):
    date: date
    records: List[AttendanceCreate]


class AttendanceUpdate(BaseModel):
    status: Optional[AttendanceStatus] = None
    remarks: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: Optional[int] = None
    employee_id: Optional[int] = None
    marked_by_id: Optional[int] = None
    student_name: Optional[str] = None
    employee_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AttendanceFilter(BaseModel):
    student_id: Optional[int] = None
    employee_id: Optional[int] = None
    department_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    status: Optional[AttendanceStatus] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=200)
    sort_by: Optional[str] = "date"
    sort_order: Optional[str] = "desc"


class AttendanceStats(BaseModel):
    total_days: int
    present_days: int
    absent_days: int
    late_days: int
    excused_days: int
    attendance_percentage: float
    risk_level: str


class MonthlyAttendanceReport(BaseModel):
    month: int
    year: int
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    total_students: int
    total_working_days: int
    average_attendance: float
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int