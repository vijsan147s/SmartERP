from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models import UserStatus, AttendanceStatus, FeeStatus


class DashboardStats(BaseModel):
    total_students: int
    total_employees: int
    attendance_rate: float
    pending_fees: Decimal
    total_departments: int
    active_users: int


class AttendanceTrend(BaseModel):
    month: str
    present: int
    absent: int
    late: int
    rate: float


class DepartmentStudentCount(BaseModel):
    department_id: int
    department_name: str
    student_count: int
    employee_count: int


class FeeCollectionTrend(BaseModel):
    month: str
    collected: Decimal
    pending: Decimal


class FeeStatusDistribution(BaseModel):
    paid: int
    partial: int
    pending: int


class EmployeeStudentDistribution(BaseModel):
    employees: int
    students: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    attendance_trend: List[AttendanceTrend]
    department_distribution: List[DepartmentStudentCount]
    fee_collection: List[FeeCollectionTrend]
    fee_status: FeeStatusDistribution
    employee_student_distribution: EmployeeStudentDistribution


class ReportFilter(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    department_id: Optional[int] = None
    course: Optional[str] = None
    semester: Optional[int] = None
    status: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=200)


class StudentReportRow(BaseModel):
    student_id: str
    full_name: str
    email: str
    phone: Optional[str]
    department: str
    course: str
    semester: int
    enrollment_date: date
    status: UserStatus
    attendance_percentage: Optional[float] = None
    pending_fees: Optional[Decimal] = None


class EmployeeReportRow(BaseModel):
    employee_id: str
    full_name: str
    email: str
    phone: Optional[str]
    department: str
    designation: str
    joining_date: date
    salary: Decimal
    status: UserStatus
    attendance_percentage: Optional[float] = None


class AttendanceReportRow(BaseModel):
    date: date
    student_id: Optional[str] = None
    student_name: Optional[str] = None
    employee_id: Optional[str] = None
    employee_name: Optional[str] = None
    department: str
    status: AttendanceStatus
    remarks: Optional[str] = None


class FeeReportRow(BaseModel):
    student_id: str
    student_name: str
    course: str
    academic_year: str
    semester: int
    total_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    due_date: Optional[date]
    status: FeeStatus
    last_payment_date: Optional[date] = None


class DepartmentReportRow(BaseModel):
    department_id: int
    department_name: str
    department_code: str
    head_name: Optional[str] = None
    student_count: int
    employee_count: int
    avg_attendance: Optional[float] = None
    total_fees: Optional[Decimal] = None
    collected_fees: Optional[Decimal] = None
    status: UserStatus


class AcademicPerformanceRow(BaseModel):
    student_id: str
    student_name: str
    department: str
    course: str
    semester: int
    subject_code: str
    subject_name: str
    internal_marks: int
    external_marks: int
    total_marks: int
    grade: Optional[str] = None
    is_passed: bool