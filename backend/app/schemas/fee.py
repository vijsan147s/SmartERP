from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models import FeeStatus, PaymentMethod


class FeeBase(BaseModel):
    academic_year: str = Field(..., min_length=1, max_length=20)
    semester: int = Field(..., ge=1, le=10)
    total_amount: Decimal = Field(..., ge=0)
    due_date: Optional[date] = None
    remarks: Optional[str] = None


class FeeCreate(FeeBase):
    student_id: int


class FeeUpdate(BaseModel):
    total_amount: Optional[Decimal] = Field(None, ge=0)
    due_date: Optional[date] = None
    status: Optional[FeeStatus] = None
    remarks: Optional[str] = None


class FeeResponse(FeeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    paid_amount: Decimal
    pending_amount: Decimal
    status: FeeStatus
    student_name: Optional[str] = None
    student_student_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FeeListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    student_name: str
    student_student_id: str
    course: str
    academic_year: str
    semester: int
    total_amount: Decimal
    paid_amount: Decimal
    pending_amount: Decimal
    due_date: Optional[date]
    status: FeeStatus
    created_at: datetime


class FeeFilter(BaseModel):
    student_id: Optional[int] = None
    department_id: Optional[int] = None
    academic_year: Optional[str] = None
    semester: Optional[int] = None
    status: Optional[FeeStatus] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"


class PaymentBase(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_date: date
    payment_method: PaymentMethod
    transaction_id: Optional[str] = Field(None, max_length=100)
    receipt_number: str = Field(..., min_length=1, max_length=50)
    remarks: Optional[str] = None


class PaymentCreate(PaymentBase):
    fee_id: int


class PaymentUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0)
    payment_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    transaction_id: Optional[str] = Field(None, max_length=100)
    receipt_number: Optional[str] = Field(None, min_length=1, max_length=50)
    remarks: Optional[str] = None


class PaymentResponse(PaymentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    fee_id: int
    received_by_id: Optional[int] = None
    received_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class FeeDashboardStats(BaseModel):
    total_fees: Decimal
    total_collected: Decimal
    total_pending: Decimal
    collection_rate: float
    paid_count: int
    partial_count: int
    pending_count: int