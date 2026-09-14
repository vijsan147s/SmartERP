from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, and_, extract
from app.crud.base import CRUDBase
from app.models import Attendance, Student, Employee, User, Department, AttendanceStatus
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate


class CRUDAttendance(CRUDBase[Attendance, AttendanceCreate, AttendanceUpdate]):
    def get_student_attendance(
        self, db: Session, student_id: int, date_from: date, date_to: date
    ) -> List[Attendance]:
        return db.query(Attendance).filter(
            and_(
                Attendance.student_id == student_id,
                Attendance.date >= date_from,
                Attendance.date <= date_to,
            )
        ).order_by(Attendance.date).all()

    def get_employee_attendance(
        self, db: Session, employee_id: int, date_from: date, date_to: date
    ) -> List[Attendance]:
        return db.query(Attendance).filter(
            and_(
                Attendance.employee_id == employee_id,
                Attendance.date >= date_from,
                Attendance.date <= date_to,
            )
        ).order_by(Attendance.date).all()

    def get_daily_attendance(
        self, db: Session, target_date: date, department_id: int = None
    ) -> List[Attendance]:
        query = db.query(Attendance).filter(Attendance.date == target_date)
        if department_id:
            query = query.join(Student, Attendance.student_id == Student.id, isouter=True)\
                .join(Employee, Attendance.employee_id == Employee.id, isouter=True)\
                .filter(
                    or_(
                        Student.department_id == department_id,
                        Employee.department_id == department_id,
                    )
                )
        return query.all()

    def get_monthly_stats(
        self, db: Session, student_id: int = None, employee_id: int = None,
        date_from: date = None, date_to: date = None
    ) -> dict:
        query = db.query(
            Attendance.status,
            func.count(Attendance.id).label("count")
        )
        if student_id:
            query = query.filter(Attendance.student_id == student_id)
        elif employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        if date_from:
            query = query.filter(Attendance.date >= date_from)
        if date_to:
            query = query.filter(Attendance.date <= date_to)
        
        results = query.group_by(Attendance.status).all()
        stats = {status.value: count for status, count in results}
        
        total = sum(stats.values())
        present = stats.get(AttendanceStatus.PRESENT.value, 0)
        percentage = (present / total * 100) if total > 0 else 0
        
        return {
            "total_days": total,
            "present_days": present,
            "absent_days": stats.get(AttendanceStatus.ABSENT.value, 0),
            "late_days": stats.get(AttendanceStatus.LATE.value, 0),
            "excused_days": stats.get(AttendanceStatus.EXCUSED.value, 0),
            "attendance_percentage": round(percentage, 2),
        }

    def get_department_monthly_report(
        self, db: Session, department_id: int, year: int, month: int
    ) -> dict:
        from calendar import monthrange
        _, days_in_month = monthrange(year, month)
        date_from = date(year, month, 1)
        date_to = date(year, month, days_in_month)
        
        students = db.query(Student).filter(Student.department_id == department_id).all()
        
        total_working_days = days_in_month
        total_students = len(students)
        
        if total_students == 0:
            return {
                "total_students": 0,
                "total_working_days": total_working_days,
                "average_attendance": 0,
                "low_risk_count": 0,
                "medium_risk_count": 0,
                "high_risk_count": 0,
            }
        
        attendance_data = db.query(
            Attendance.student_id,
            Attendance.status,
            func.count(Attendance.id).label("count")
        ).filter(
            and_(
                Attendance.student_id.in_([s.id for s in students]),
                Attendance.date >= date_from,
                Attendance.date <= date_to,
            )
        ).group_by(Attendance.student_id, Attendance.status).all()
        
        student_stats = {}
        for student_id, status, count in attendance_data:
            if student_id not in student_stats:
                student_stats[student_id] = {}
            student_stats[student_id][status.value] = count
        
        total_attendance = 0
        low_risk = medium_risk = high_risk = 0
        
        for student in students:
            stats = student_stats.get(student.id, {})
            total_days = sum(stats.values())
            present = stats.get(AttendanceStatus.PRESENT.value, 0)
            percentage = (present / total_days * 100) if total_days > 0 else 0
            total_attendance += percentage
            
            if percentage > 75:
                low_risk += 1
            elif percentage >= 60:
                medium_risk += 1
            else:
                high_risk += 1
        
        return {
            "total_students": total_students,
            "total_working_days": total_working_days,
            "average_attendance": round(total_attendance / total_students, 2),
            "low_risk_count": low_risk,
            "medium_risk_count": medium_risk,
            "high_risk_count": high_risk,
        }

    def bulk_create(self, db: Session, records: List[AttendanceCreate]) -> List[Attendance]:
        db_objects = [Attendance(**r.model_dump()) for r in records]
        db.add_all(db_objects)
        db.commit()
        for obj in db_objects:
            db.refresh(obj)
        return db_objects


crud_attendance = CRUDAttendance(Attendance)