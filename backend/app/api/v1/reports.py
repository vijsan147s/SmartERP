from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from io import StringIO
import csv
from app.api.deps import get_db, require_manager, require_employee
from app.crud import crud_student, crud_employee, crud_department, crud_fee, crud_attendance, crud_result
from app.models import User, UserStatus, AttendanceStatus, FeeStatus, Student, Employee, Department, Fee, Payment, Result, Subject
from app.schemas.report import (
    DashboardResponse, DashboardStats, AttendanceTrend, DepartmentStudentCount,
    FeeCollectionTrend, FeeStatusDistribution, EmployeeStudentDistribution,
    StudentReportRow, EmployeeReportRow, AttendanceReportRow, FeeReportRow,
    DepartmentReportRow, AcademicPerformanceRow
)
from sqlalchemy import func, extract, and_, or_, Integer

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse, dependencies=[Depends(require_employee)])
def get_dashboard(db: Session = Depends(get_db)):
    total_students = crud_student.get_active_count(db)
    total_employees = crud_employee.get_active_count(db)
    total_departments = db.query(Department).filter(Department.status == UserStatus.ACTIVE).count()
    active_users = db.query(User).filter(User.status == UserStatus.ACTIVE).count()
    
    fee_stats = crud_fee.get_dashboard_stats(db)
    
    attendance_subq = db.query(
        func.count(crud_attendance.model.id).filter(crud_attendance.model.status == AttendanceStatus.PRESENT).label("present"),
        func.count(crud_attendance.model.id).label("total")
    ).first()
    
    attendance_rate = 0.0
    if attendance_subq and attendance_subq.total > 0:
        attendance_rate = round(attendance_subq.present / attendance_subq.total * 100, 2)
    
    stats = DashboardStats(
        total_students=total_students,
        total_employees=total_employees,
        attendance_rate=attendance_rate,
        pending_fees=fee_stats["total_pending"],
        total_departments=total_departments,
        active_users=total_students + total_employees,
    )
    
    attendance_trend = []
    for i in range(6):
        month_date = date.today().replace(day=1)
        for _ in range(i):
            if month_date.month == 1:
                month_date = month_date.replace(year=month_date.year-1, month=12)
            else:
                month_date = month_date.replace(month=month_date.month-1)
        
        month_start = month_date
        if month_date.month == 12:
            month_end = month_date.replace(year=month_date.year+1, month=1, day=1)
        else:
            month_end = month_date.replace(month=month_date.month+1, day=1)
        
        present = db.query(crud_attendance.model).filter(
            and_(
                crud_attendance.model.status == AttendanceStatus.PRESENT,
                crud_attendance.model.date >= month_start,
                crud_attendance.model.date < month_end,
            )
        ).count()
        
        total = db.query(crud_attendance.model).filter(
            and_(
                crud_attendance.model.date >= month_start,
                crud_attendance.model.date < month_end,
            )
        ).count()
        
        rate = round(present / total * 100, 2) if total > 0 else 0
        
        attendance_trend.append(AttendanceTrend(
            month=month_date.strftime("%Y-%m"),
            present=present,
            absent=total - present,
            late=0,
            rate=rate
        ))
    
    departments = crud_department.get_all_active(db)
    dept_distribution = []
    for dept in departments:
        dept_distribution.append(DepartmentStudentCount(
            department_id=dept.id,
            department_name=dept.name,
            student_count=crud_department.get_student_count(db, dept.id),
            employee_count=crud_department.get_employee_count(db, dept.id),
        ))
    
    fee_collection = crud_fee.get_monthly_collection(db, datetime.now().year)
    fee_collection_list = [
        FeeCollectionTrend(month=m["month"], collected=Decimal(str(m["collected"])), pending=Decimal("0"))
        for m in fee_collection
    ]
    
    fee_status = FeeStatusDistribution(
        paid=fee_stats["paid_count"],
        partial=fee_stats["partial_count"],
        pending=fee_stats["pending_count"],
    )
    
    emp_student_dist = EmployeeStudentDistribution(
        employees=total_employees,
        students=total_students,
    )
    
    return DashboardResponse(
        stats=stats,
        attendance_trend=list(reversed(attendance_trend)),
        department_distribution=dept_distribution,
        fee_collection=fee_collection_list,
        fee_status=fee_status,
        employee_student_distribution=emp_student_dist,
    )


def export_csv(rows: List, headers: List[str], filename: str) -> Response:
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow([getattr(row, h.lower().replace(" ", "_"), "") for h in headers])
    
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/students", response_model=List[StudentReportRow], dependencies=[Depends(require_manager)])
def get_student_report(
    department_id: Optional[int] = None,
    course: Optional[str] = None,
    semester: Optional[int] = None,
    status: Optional[str] = None,
    export: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Student).options(
        joinedload(Student.user),
        joinedload(Student.department)
    )
    
    if department_id:
        query = query.filter(Student.department_id == department_id)
    if course:
        query = query.filter(Student.course == course)
    if semester:
        query = query.filter(Student.semester == semester)
    if status:
        query = query.filter(Student.status == status)
    
    students = query.all()
    
    rows = []
    for s in students:
        attendance_stats = crud_attendance.get_monthly_stats(db, student_id=s.id)
        fee = db.query(Fee).filter(Fee.student_id == s.id).first()
        
        rows.append(StudentReportRow(
            student_id=s.student_id,
            full_name=s.user.full_name,
            email=s.user.email,
            phone=s.user.phone,
            department=s.department.name if s.department else "N/A",
            course=s.course,
            semester=s.semester,
            enrollment_date=s.enrollment_date,
            status=s.status,
            attendance_percentage=attendance_stats["attendance_percentage"],
            pending_fees=fee.pending_amount if fee else None,
        ))
    
    if export:
        return export_csv(rows, [
            "Student ID", "Full Name", "Email", "Phone", "Department",
            "Course", "Semester", "Enrollment Date", "Status",
            "Attendance %", "Pending Fees"
        ], "student_report.csv")
    
    return rows


@router.get("/employees", response_model=List[EmployeeReportRow], dependencies=[Depends(require_manager)])
def get_employee_report(
    department_id: Optional[int] = None,
    designation: Optional[str] = None,
    status: Optional[str] = None,
    export: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Employee).options(
        joinedload(Employee.user),
        joinedload(Employee.department)
    )
    
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    if designation:
        query = query.filter(Employee.designation == designation)
    if status:
        query = query.filter(Employee.status == status)
    
    employees = query.all()
    
    rows = []
    for e in employees:
        attendance_stats = crud_attendance.get_monthly_stats(db, employee_id=e.id)
        
        rows.append(EmployeeReportRow(
            employee_id=e.employee_id,
            full_name=e.user.full_name,
            email=e.user.email,
            phone=e.user.phone,
            department=e.department.name if e.department else "N/A",
            designation=e.designation,
            joining_date=e.joining_date,
            salary=e.salary,
            status=e.status,
            attendance_percentage=attendance_stats["attendance_percentage"],
        ))
    
    if export:
        return export_csv(rows, [
            "Employee ID", "Full Name", "Email", "Phone", "Department",
            "Designation", "Joining Date", "Salary", "Status", "Attendance %"
        ], "employee_report.csv")
    
    return rows


@router.get("/attendance", response_model=List[AttendanceReportRow], dependencies=[Depends(require_manager)])
def get_attendance_report(
    department_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[str] = None,
    export: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(crud_attendance.model).options(
        joinedload(crud_attendance.model.student).joinedload(Student.user),
        joinedload(crud_attendance.model.student).joinedload(Student.department),
        joinedload(crud_attendance.model.employee).joinedload(Employee.user),
        joinedload(crud_attendance.model.employee).joinedload(Employee.department),
    )
    
    if date_from:
        query = query.filter(crud_attendance.model.date >= date_from)
    if date_to:
        query = query.filter(crud_attendance.model.date <= date_to)
    if status:
        query = query.filter(crud_attendance.model.status == status)
    if department_id:
        query = query.filter(
            or_(
                Student.department_id == department_id,
                Employee.department_id == department_id,
            )
        ).join(Student, crud_attendance.model.student_id == Student.id, isouter=True)\
         .join(Employee, crud_attendance.model.employee_id == Employee.id, isouter=True)
    
    records = query.order_by(crud_attendance.model.date.desc()).all()
    
    rows = []
    for r in records:
        if r.student:
            rows.append(AttendanceReportRow(
                date=r.date,
                student_id=r.student.student_id,
                student_name=r.student.user.full_name,
                department=r.student.department.name if r.student.department else "N/A",
                status=r.status,
                remarks=r.remarks,
            ))
        elif r.employee:
            rows.append(AttendanceReportRow(
                date=r.date,
                employee_id=r.employee.employee_id,
                employee_name=r.employee.user.full_name,
                department=r.employee.department.name if r.employee.department else "N/A",
                status=r.status,
                remarks=r.remarks,
            ))
    
    if export:
        return export_csv(rows, [
            "Date", "Student ID", "Student Name", "Employee ID", "Employee Name",
            "Department", "Status", "Remarks"
        ], "attendance_report.csv")
    
    return rows


@router.get("/fees", response_model=List[FeeReportRow], dependencies=[Depends(require_manager)])
def get_fee_report(
    department_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None,
    status: Optional[str] = None,
    export: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Fee).options(
        joinedload(Fee.student).joinedload(Student.user),
        joinedload(Fee.student).joinedload(Student.department),
        joinedload(Fee.payments)
    )
    
    if department_id:
        query = query.join(Student).filter(Student.department_id == department_id)
    if academic_year:
        query = query.filter(Fee.academic_year == academic_year)
    if semester:
        query = query.filter(Fee.semester == semester)
    if status:
        query = query.filter(Fee.status == status)
    
    fees = query.all()
    
    rows = []
    for f in fees:
        last_payment = max(f.payments, key=lambda p: p.payment_date) if f.payments else None
        
        rows.append(FeeReportRow(
            student_id=f.student.student_id,
            student_name=f.student.user.full_name,
            course=f.student.course,
            academic_year=f.academic_year,
            semester=f.semester,
            total_amount=f.total_amount,
            paid_amount=f.paid_amount,
            pending_amount=f.pending_amount,
            due_date=f.due_date,
            status=f.status,
            last_payment_date=last_payment.payment_date if last_payment else None,
        ))
    
    if export:
        return export_csv(rows, [
            "Student ID", "Student Name", "Course", "Academic Year", "Semester",
            "Total Amount", "Paid Amount", "Pending Amount", "Due Date", "Status", "Last Payment Date"
        ], "fee_report.csv")
    
    return rows


@router.get("/departments", response_model=List[DepartmentReportRow], dependencies=[Depends(require_manager)])
def get_department_report(
    status: Optional[str] = None,
    export: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Department).options(joinedload(Department.head).joinedload(Employee.user))
    
    if status:
        query = query.filter(Department.status == status)
    
    departments = query.all()
    
    rows = []
    for d in departments:
        total_fees = db.query(func.sum(Fee.total_amount)).join(Student).filter(
            Student.department_id == d.id
        ).scalar() or Decimal("0")
        
        collected_fees = db.query(func.sum(Fee.paid_amount)).join(Student).filter(
            Student.department_id == d.id
        ).scalar() or Decimal("0")
        
        avg_attendance = db.query(
            func.avg(func.cast(crud_attendance.model.status == AttendanceStatus.PRESENT, type_=Integer))
        ).join(
            Student, crud_attendance.model.student_id == Student.id
        ).filter(Student.department_id == d.id).scalar() or 0
        
        rows.append(DepartmentReportRow(
            department_id=d.id,
            department_name=d.name,
            department_code=d.code,
            head_name=d.head.user.full_name if d.head and d.head.user else None,
            student_count=crud_department.get_student_count(db, d.id),
            employee_count=crud_department.get_employee_count(db, d.id),
            avg_attendance=round(float(avg_attendance) * 100, 2) if avg_attendance else None,
            total_fees=total_fees,
            collected_fees=collected_fees,
            status=d.status,
        ))
    
    if export:
        return export_csv(rows, [
            "Department ID", "Department Name", "Department Code", "Head Name",
            "Student Count", "Employee Count", "Avg Attendance %", "Total Fees", "Collected Fees", "Status"
        ], "department_report.csv")
    
    return rows


@router.get("/academic-performance", response_model=List[AcademicPerformanceRow], dependencies=[Depends(require_manager)])
def get_academic_performance_report(
    department_id: Optional[int] = None,
    course: Optional[str] = None,
    semester: Optional[int] = None,
    export: bool = False,
    db: Session = Depends(get_db)
):
    query = db.query(Result).options(
        joinedload(Result.student).joinedload(Student.user),
        joinedload(Result.student).joinedload(Student.department),
        joinedload(Result.subject)
    )
    
    if department_id:
        query = query.join(Student).filter(Student.department_id == department_id)
    if course:
        query = query.join(Student).filter(Student.course == course)
    if semester:
        query = query.filter(Result.semester == semester)
    
    results = query.all()
    
    rows = []
    for r in results:
        rows.append(AcademicPerformanceRow(
            student_id=r.student.student_id,
            student_name=r.student.user.full_name,
            department=r.student.department.name if r.student.department else "N/A",
            course=r.student.course,
            semester=r.semester,
            subject_code=r.subject.code,
            subject_name=r.subject.name,
            internal_marks=r.internal_marks,
            external_marks=r.external_marks,
            total_marks=r.total_marks,
            grade=r.grade.value if r.grade else None,
            is_passed=r.is_passed,
        ))
    
    if export:
        return export_csv(rows, [
            "Student ID", "Student Name", "Department", "Course", "Semester",
            "Subject Code", "Subject Name", "Internal Marks", "External Marks",
            "Total Marks", "Grade", "Passed"
        ], "academic_performance_report.csv")
    
    return rows