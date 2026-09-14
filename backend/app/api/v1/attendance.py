from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date, datetime
from app.api.deps import get_db, require_manager, require_employee, require_student
from app.crud import crud_attendance, crud_student, crud_employee
from app.schemas.attendance import (
    AttendanceCreate, AttendanceUpdate, AttendanceResponse, AttendanceFilter,
    AttendanceStats, MonthlyAttendanceReport, AttendanceBulkCreate
)
from app.schemas.auth import PaginatedResponse
from app.models import AttendanceStatus, User

router = APIRouter()


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_manager)])
def mark_attendance(attendance: AttendanceCreate, db: Session = Depends(get_db)):
    if attendance.student_id:
        student = crud_student.get(db, attendance.student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        existing = db.query(crud_attendance.model).filter(
            crud_attendance.model.student_id == attendance.student_id,
            crud_attendance.model.date == attendance.date
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Attendance already marked for this student on this date")
    elif attendance.employee_id:
        employee = crud_employee.get(db, attendance.employee_id)
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")
        existing = db.query(crud_attendance.model).filter(
            crud_attendance.model.employee_id == attendance.employee_id,
            crud_attendance.model.date == attendance.date
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Attendance already marked for this employee on this date")
    else:
        raise HTTPException(status_code=400, detail="Either student_id or employee_id must be provided")
    
    return crud_attendance.create(db, obj_in=attendance)


@router.post("/bulk", response_model=List[AttendanceResponse], dependencies=[Depends(require_manager)])
def bulk_mark_attendance(bulk_data: AttendanceBulkCreate, db: Session = Depends(get_db)):
    return crud_attendance.bulk_create(db, bulk_data.records)


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_employee)])
def get_attendance(
    student_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    department_id: Optional[int] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    sort_by: str = "date",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    from app.crud.attendance import crud_attendance as crud
    from sqlalchemy.orm import joinedload
    from app.models import Student, Employee, User
    
    query = db.query(crud_attendance.model).options(
        joinedload(crud_attendance.model.student).joinedload(Student.user),
        joinedload(crud_attendance.model.employee).joinedload(Employee.user)
    )
    
    if student_id:
        query = query.filter(crud_attendance.model.student_id == student_id)
    if employee_id:
        query = query.filter(crud_attendance.model.employee_id == employee_id)
    if department_id:
        query = query.join(Student, crud_attendance.model.student_id == Student.id, isouter=True)\
            .join(Employee, crud_attendance.model.employee_id == Employee.id, isouter=True)\
            .filter(
                (Student.department_id == department_id) | (Employee.department_id == department_id)
            )
    if date_from:
        query = query.filter(crud_attendance.model.date >= date_from)
    if date_to:
        query = query.filter(crud_attendance.model.date <= date_to)
    if status:
        query = query.filter(crud_attendance.model.status == status)
    
    if sort_order == "desc":
        query = query.order_by(getattr(crud_attendance.model, sort_by).desc())
    else:
        query = query.order_by(getattr(crud_attendance.model, sort_by).asc())
    
    total = query.count()
    records = query.offset((page-1)*page_size).limit(page_size).all()
    
    items = []
    for r in records:
        items.append(AttendanceResponse(
            id=r.id,
            student_id=r.student_id,
            employee_id=r.employee_id,
            date=r.date,
            status=r.status,
            remarks=r.remarks,
            marked_by_id=r.marked_by_id,
            student_name=r.student.user.full_name if r.student and r.student.user else None,
            employee_name=r.employee.user.full_name if r.employee and r.employee.user else None,
            created_at=r.created_at,
            updated_at=r.updated_at,
        ))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/daily", dependencies=[Depends(require_employee)])
def get_daily_attendance(
    date: date = Query(default_factory=date.today),
    department_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    records = crud_attendance.get_daily_attendance(db, date, department_id)
    return [
        AttendanceResponse(
            id=r.id,
            student_id=r.student_id,
            employee_id=r.employee_id,
            date=r.date,
            status=r.status,
            remarks=r.remarks,
            marked_by_id=r.marked_by_id,
            student_name=r.student.user.full_name if r.student and r.student.user else None,
            employee_name=r.employee.user.full_name if r.employee and r.employee.user else None,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        for r in records
    ]


@router.get("/stats/student/{student_id}", response_model=AttendanceStats, dependencies=[Depends(require_employee)])
def get_student_attendance_stats(
    student_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    student = crud_student.get(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    stats = crud_attendance.get_monthly_stats(db, student_id=student_id, date_from=date_from, date_to=date_to)
    
    percentage = stats["attendance_percentage"]
    if percentage > 75:
        risk = "LOW"
    elif percentage >= 60:
        risk = "MEDIUM"
    else:
        risk = "HIGH"
    
    return AttendanceStats(
        total_days=stats["total_days"],
        present_days=stats["present_days"],
        absent_days=stats["absent_days"],
        late_days=stats["late_days"],
        excused_days=stats["excused_days"],
        attendance_percentage=percentage,
        risk_level=risk
    )


@router.get("/stats/employee/{employee_id}", response_model=AttendanceStats, dependencies=[Depends(require_manager)])
def get_employee_attendance_stats(
    employee_id: int,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    employee = crud_employee.get(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    stats = crud_attendance.get_monthly_stats(db, employee_id=employee_id, date_from=date_from, date_to=date_to)
    
    percentage = stats["attendance_percentage"]
    if percentage > 75:
        risk = "LOW"
    elif percentage >= 60:
        risk = "MEDIUM"
    else:
        risk = "HIGH"
    
    return AttendanceStats(
        total_days=stats["total_days"],
        present_days=stats["present_days"],
        absent_days=stats["absent_days"],
        late_days=stats["late_days"],
        excused_days=stats["excused_days"],
        attendance_percentage=percentage,
        risk_level=risk
    )


@router.get("/report/monthly", response_model=MonthlyAttendanceReport, dependencies=[Depends(require_manager)])
def get_monthly_attendance_report(
    department_id: int,
    year: int = Query(default_factory=lambda: datetime.now().year),
    month: int = Query(default_factory=lambda: datetime.now().month, ge=1, le=12),
    db: Session = Depends(get_db)
):
    report = crud_attendance.get_department_monthly_report(db, department_id, year, month)
    from app.crud import crud_department
    dept = crud_department.get(db, department_id)
    
    return MonthlyAttendanceReport(
        month=month,
        year=year,
        department_id=department_id,
        department_name=dept.name if dept else None,
        **report
    )


@router.get("/me/stats", response_model=AttendanceStats, dependencies=[Depends(require_student)])
def get_my_attendance_stats(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = crud_student.get_by_user_id(db, current_user.id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return get_student_attendance_stats(student.id, date_from, date_to, db)


@router.put("/{attendance_id}", response_model=AttendanceResponse, dependencies=[Depends(require_manager)])
def update_attendance(attendance_id: int, attendance_update: AttendanceUpdate, db: Session = Depends(get_db)):
    attendance = crud_attendance.get(db, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    return crud_attendance.update(db, db_obj=attendance, obj_in=attendance_update)


@router.delete("/{attendance_id}", dependencies=[Depends(require_manager)])
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    attendance = crud_attendance.get(db, attendance_id)
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    crud_attendance.remove(db, id=attendance_id)
    return {"message": "Attendance deleted successfully"}