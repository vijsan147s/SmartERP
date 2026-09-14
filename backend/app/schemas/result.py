from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from app.models import Grade


class SubjectBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    department_id: Optional[int] = None
    credits: int = Field(3, ge=1, le=6)
    max_internal_marks: int = Field(30, ge=1, le=100)
    max_external_marks: int = Field(70, ge=1, le=100)
    semester: int = Field(..., ge=1, le=10)

    @field_validator("code")
    @classmethod
    def code_upper(cls, v):
        return v.upper().strip()


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    department_id: Optional[int] = None
    credits: Optional[int] = Field(None, ge=1, le=6)
    max_internal_marks: Optional[int] = Field(None, ge=1, le=100)
    max_external_marks: Optional[int] = Field(None, ge=1, le=100)
    semester: Optional[int] = Field(None, ge=1, le=10)
    is_active: Optional[bool] = None


class SubjectResponse(SubjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    department_name: Optional[str] = None


class SubjectFilter(BaseModel):
    search: Optional[str] = None
    department_id: Optional[int] = None
    semester: Optional[int] = None
    is_active: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = "code"
    sort_order: Optional[str] = "asc"


class ResultBase(BaseModel):
    internal_marks: int = Field(..., ge=0)
    external_marks: int = Field(..., ge=0)
    exam_date: Optional[date] = None
    remarks: Optional[str] = None


class ResultCreate(ResultBase):
    student_id: int
    subject_id: int
    semester: int = Field(..., ge=1, le=10)

    @field_validator("internal_marks")
    @classmethod
    def validate_internal_marks(cls, v, info):
        return v

    @field_validator("external_marks")
    @classmethod
    def validate_external_marks(cls, v, info):
        return v


class ResultUpdate(BaseModel):
    internal_marks: Optional[int] = Field(None, ge=0)
    external_marks: Optional[int] = Field(None, ge=0)
    exam_date: Optional[date] = None
    remarks: Optional[str] = None


class ResultResponse(ResultBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    subject_id: int
    semester: int
    total_marks: int
    grade: Optional[Grade] = None
    is_passed: bool
    student_name: Optional[str] = None
    student_student_id: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    max_internal_marks: int
    max_external_marks: int
    created_at: datetime
    updated_at: datetime


class ResultListResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    student_name: str
    student_student_id: str
    subject_id: int
    subject_name: str
    subject_code: str
    semester: int
    internal_marks: int
    external_marks: int
    total_marks: int
    grade: Optional[Grade] = None
    is_passed: bool
    created_at: datetime


class ResultFilter(BaseModel):
    student_id: Optional[int] = None
    subject_id: Optional[int] = None
    department_id: Optional[int] = None
    semester: Optional[int] = None
    grade: Optional[Grade] = None
    is_passed: Optional[bool] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"


class StudentResultSummary(BaseModel):
    student_id: int
    student_name: str
    student_student_id: str
    semester: int
    subjects: List[ResultResponse]
    total_marks: int
    average_percentage: float
    overall_grade: Optional[Grade] = None
    passed_count: int
    failed_count: int