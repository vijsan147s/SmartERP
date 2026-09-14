from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum, ForeignKey, Table, UniqueConstraint, Index, Text, Date, Numeric
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.sql import func
from app.core.database import Base
import enum
from datetime import datetime


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    EMPLOYEE = "EMPLOYEE"
    STUDENT = "STUDENT"


class UserStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(SQLEnum(UserRole), unique=True, nullable=False, index=True)
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    users = relationship("User", secondary=user_roles, back_populates="roles")

    def __repr__(self):
        return f"<Role(name='{self.name}')>"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    is_superuser = Column(Boolean, default=False, nullable=False)

    roles = relationship("Role", secondary=user_roles, back_populates="users")
    student = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    employee = relationship("Employee", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(email='{self.email}', username='{self.username}')>"


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    head_id = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    head = relationship("Employee", foreign_keys=[head_id], back_populates="managed_department")
    students = relationship("Student", back_populates="department")
    employees = relationship("Employee", back_populates="department", foreign_keys="Employee.department_id")

    __table_args__ = (
        Index("ix_departments_name_status", "name", "status"),
    )

    def __repr__(self):
        return f"<Department(name='{self.name}', code='{self.code}')>"


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    course = Column(String(100), nullable=False)
    semester = Column(Integer, default=1, nullable=False)
    enrollment_date = Column(Date, nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    user = relationship("User", back_populates="student")
    department = relationship("Department", back_populates="students")
    attendances = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    fees = relationship("Fee", back_populates="student", cascade="all, delete-orphan")
    results = relationship("Result", back_populates="student", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_students_dept_course_sem", "department_id", "course", "semester"),
        Index("ix_students_status", "status"),
    )

    def __repr__(self):
        return f"<Student(student_id='{self.student_id}', course='{self.course}')>"


class Employee(Base, TimestampMixin):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(50), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    designation = Column(String(100), nullable=False)
    joining_date = Column(Date, nullable=False)
    salary = Column(Numeric(12, 2), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    emergency_contact = Column(String(255), nullable=True)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)

    user = relationship("User", back_populates="employee")
    department = relationship("Department", back_populates="employees", foreign_keys=[department_id])
    managed_department = relationship("Department", back_populates="head", foreign_keys=[Department.head_id])
    attendances = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_employees_dept_designation", "department_id", "designation"),
        Index("ix_employees_status", "status"),
    )

    def __repr__(self):
        return f"<Employee(employee_id='{self.employee_id}', designation='{self.designation}')>"


class AttendanceStatus(str, enum.Enum):
    PRESENT = "PRESENT"
    ABSENT = "ABSENT"
    LATE = "LATE"
    EXCUSED = "EXCUSED"


class Attendance(Base, TimestampMixin):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    status = Column(SQLEnum(AttendanceStatus), nullable=False)
    remarks = Column(Text, nullable=True)
    marked_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    student = relationship("Student", back_populates="attendances")
    employee = relationship("Employee", back_populates="attendances")
    marked_by = relationship("User")

    __table_args__ = (
        UniqueConstraint("student_id", "date", name="uq_student_date_attendance"),
        UniqueConstraint("employee_id", "date", name="uq_employee_date_attendance"),
        Index("ix_attendance_student_date", "student_id", "date"),
        Index("ix_attendance_employee_date", "employee_id", "date"),
        Index("ix_attendance_date_status", "date", "status"),
    )

    def __repr__(self):
        entity = self.student_id or self.employee_id
        return f"<Attendance(entity_id={entity}, date='{self.date}', status='{self.status}')>"


class FeeStatus(str, enum.Enum):
    PAID = "PAID"
    PARTIAL = "PARTIAL"
    PENDING = "PENDING"


class Fee(Base, TimestampMixin):
    __tablename__ = "fees"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    academic_year = Column(String(20), nullable=False)
    semester = Column(Integer, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    paid_amount = Column(Numeric(12, 2), default=0, nullable=False)
    pending_amount = Column(Numeric(12, 2), nullable=False)
    due_date = Column(Date, nullable=True)
    status = Column(SQLEnum(FeeStatus), default=FeeStatus.PENDING, nullable=False)
    remarks = Column(Text, nullable=True)

    student = relationship("Student", back_populates="fees")
    payments = relationship("Payment", back_populates="fee", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("student_id", "academic_year", "semester", name="uq_student_year_sem_fee"),
        Index("ix_fees_status", "status"),
        Index("ix_fees_due_date", "due_date"),
    )

    def __repr__(self):
        return f"<Fee(student_id={self.student_id}, total={self.total_amount}, status='{self.status}')>"


class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CARD = "CARD"
    UPI = "UPI"
    BANK_TRANSFER = "BANK_TRANSFER"
    CHEQUE = "CHEQUE"
    ONLINE = "ONLINE"


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    fee_id = Column(Integer, ForeignKey("fees.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    payment_date = Column(Date, nullable=False, index=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    transaction_id = Column(String(100), unique=True, nullable=True)
    receipt_number = Column(String(50), unique=True, nullable=False, index=True)
    remarks = Column(Text, nullable=True)
    received_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    fee = relationship("Fee", back_populates="payments")
    received_by = relationship("User")

    __table_args__ = (
        Index("ix_payments_fee_date", "fee_id", "payment_date"),
    )

    def __repr__(self):
        return f"<Payment(fee_id={self.fee_id}, amount={self.amount}, method='{self.payment_method}')>"


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    credits = Column(Integer, default=3, nullable=False)
    max_internal_marks = Column(Integer, default=30, nullable=False)
    max_external_marks = Column(Integer, default=70, nullable=False)
    semester = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    department = relationship("Department")
    results = relationship("Result", back_populates="subject")

    __table_args__ = (
        Index("ix_subjects_dept_sem", "department_id", "semester"),
    )

    def __repr__(self):
        return f"<Subject(code='{self.code}', name='{self.name}')>"


class Grade(str, enum.Enum):
    A_PLUS = "A+"
    A = "A"
    B_PLUS = "B+"
    B = "B"
    C = "C"
    F = "F"


class Result(Base, TimestampMixin):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    semester = Column(Integer, nullable=False)
    internal_marks = Column(Integer, default=0, nullable=False)
    external_marks = Column(Integer, default=0, nullable=False)
    total_marks = Column(Integer, default=0, nullable=False)
    grade = Column(SQLEnum(Grade), nullable=True)
    is_passed = Column(Boolean, default=False, nullable=False)
    exam_date = Column(Date, nullable=True)
    remarks = Column(Text, nullable=True)

    student = relationship("Student", back_populates="results")
    subject = relationship("Subject", back_populates="results")

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "semester", name="uq_student_subject_sem_result"),
        Index("ix_results_student_sem", "student_id", "semester"),
    )

    def __repr__(self):
        return f"<Result(student_id={self.student_id}, subject_id={self.subject_id}, total={self.total_marks}, grade='{self.grade}')>"