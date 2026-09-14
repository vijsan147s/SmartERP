from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, and_
from app.crud.base import CRUDBase
from app.models import Result, Subject, Student, Grade
from app.schemas.result import ResultCreate, ResultUpdate, SubjectCreate, SubjectUpdate


class CRUDSubject(CRUDBase[Subject, SubjectCreate, SubjectUpdate]):
    def get_by_code(self, db: Session, code: str) -> Optional[Subject]:
        return db.query(Subject).filter(Subject.code == code).first()

    def get_multi_with_department(
        self, db: Session, *, skip: int = 0, limit: int = 100, filters: dict = None
    ) -> List[Subject]:
        query = db.query(Subject).options(joinedload(Subject.department))
        if filters:
            if filters.get("search"):
                search = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Subject.code.ilike(search),
                        Subject.name.ilike(search),
                    )
                )
            if filters.get("department_id"):
                query = query.filter(Subject.department_id == filters["department_id"])
            if filters.get("semester"):
                query = query.filter(Subject.semester == filters["semester"])
            if filters.get("is_active") is not None:
                query = query.filter(Subject.is_active == filters["is_active"])
        return query.order_by(Subject.code).offset(skip).limit(limit).all()

    def get_by_department_semester(self, db: Session, department_id: int, semester: int) -> List[Subject]:
        return db.query(Subject).filter(
            and_(
                Subject.department_id == department_id,
                Subject.semester == semester,
                Subject.is_active == True,
            )
        ).all()


class CRUDResult(CRUDBase[Result, ResultCreate, ResultUpdate]):
    def get_by_student_subject_sem(
        self, db: Session, student_id: int, subject_id: int, semester: int
    ) -> Optional[Result]:
        return db.query(Result).filter(
            and_(
                Result.student_id == student_id,
                Result.subject_id == subject_id,
                Result.semester == semester,
            )
        ).first()

    def get_with_details(self, db: Session, id: int) -> Optional[Result]:
        return db.query(Result).options(
            joinedload(Result.student).joinedload(Student.user),
            joinedload(Result.student).joinedload(Student.department),
            joinedload(Result.subject)
        ).filter(Result.id == id).first()

    def get_multi_with_details(
        self, db: Session, *, skip: int = 0, limit: int = 100, filters: dict = None
    ) -> List[Result]:
        query = db.query(Result).options(
            joinedload(Result.student).joinedload(Student.user),
            joinedload(Result.student).joinedload(Student.department),
            joinedload(Result.subject)
        )
        if filters:
            if filters.get("student_id"):
                query = query.filter(Result.student_id == filters["student_id"])
            if filters.get("subject_id"):
                query = query.filter(Result.subject_id == filters["subject_id"])
            if filters.get("department_id"):
                query = query.join(Student).filter(Student.department_id == filters["department_id"])
            if filters.get("semester"):
                query = query.filter(Result.semester == filters["semester"])
            if filters.get("grade"):
                query = query.filter(Result.grade == filters["grade"])
            if filters.get("is_passed") is not None:
                query = query.filter(Result.is_passed == filters["is_passed"])
        return query.order_by(Result.created_at.desc()).offset(skip).limit(limit).all()

    def get_count_with_filters(self, db: Session, filters: dict = None) -> int:
        query = db.query(Result)
        if filters:
            if filters.get("student_id"):
                query = query.filter(Result.student_id == filters["student_id"])
            if filters.get("subject_id"):
                query = query.filter(Result.subject_id == filters["subject_id"])
            if filters.get("department_id"):
                query = query.join(Student).filter(Student.department_id == filters["department_id"])
            if filters.get("semester"):
                query = query.filter(Result.semester == filters["semester"])
            if filters.get("grade"):
                query = query.filter(Result.grade == filters["grade"])
            if filters.get("is_passed") is not None:
                query = query.filter(Result.is_passed == filters["is_passed"])
        return query.count()

    def get_student_summary(self, db: Session, student_id: int, semester: int) -> dict:
        results = db.query(Result).options(joinedload(Result.subject)).filter(
            and_(
                Result.student_id == student_id,
                Result.semester == semester,
            )
        ).all()
        
        if not results:
            return {
                "subjects": [],
                "total_marks": 0,
                "average_percentage": 0,
                "overall_grade": None,
                "passed_count": 0,
                "failed_count": 0,
            }
        
        total_marks = sum(r.total_marks for r in results)
        max_possible = sum(r.subject.max_internal_marks + r.subject.max_external_marks for r in results)
        average = (total_marks / max_possible * 100) if max_possible > 0 else 0
        
        passed = sum(1 for r in results if r.is_passed)
        failed = len(results) - passed
        
        overall_grade = self._calculate_grade(average)
        
        return {
            "subjects": results,
            "total_marks": total_marks,
            "average_percentage": round(average, 2),
            "overall_grade": overall_grade,
            "passed_count": passed,
            "failed_count": failed,
        }

    def _calculate_grade(self, percentage: float) -> Optional[Grade]:
        if percentage >= 90:
            return Grade.A_PLUS
        elif percentage >= 80:
            return Grade.A
        elif percentage >= 70:
            return Grade.B_PLUS
        elif percentage >= 60:
            return Grade.B
        elif percentage >= 50:
            return Grade.C
        else:
            return Grade.F

    def calculate_total_and_grade(
        self, internal_marks: int, external_marks: int, 
        max_internal: int, max_external: int
    ) -> dict:
        total = internal_marks + external_marks
        max_total = max_internal + max_external
        percentage = (total / max_total * 100) if max_total > 0 else 0
        
        grade = self._calculate_grade(percentage)
        is_passed = percentage >= 50
        
        return {
            "total_marks": total,
            "grade": grade,
            "is_passed": is_passed,
        }


crud_subject = CRUDSubject(Subject)
crud_result = CRUDResult(Result)