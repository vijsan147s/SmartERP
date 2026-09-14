from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, and_
from app.crud.base import CRUDBase
from app.models import Student, User, Department, UserStatus
from app.schemas.student import StudentCreate, StudentUpdate


class CRUDStudent(CRUDBase[Student, StudentCreate, StudentUpdate]):
    def get_by_student_id(self, db: Session, student_id: str) -> Optional[Student]:
        return db.query(Student).filter(Student.student_id == student_id).first()

    def get_by_user_id(self, db: Session, user_id: int) -> Optional[Student]:
        return db.query(Student).filter(Student.user_id == user_id).first()

    def get_with_details(self, db: Session, id: int) -> Optional[Student]:
        return db.query(Student).options(
            joinedload(Student.user),
            joinedload(Student.department)
        ).filter(Student.id == id).first()

    def get_multi_with_details(
        self, db: Session, *, skip: int = 0, limit: int = 100, filters: dict = None
    ) -> List[Student]:
        query = db.query(Student).options(
            joinedload(Student.user),
            joinedload(Student.department)
        )
        if filters:
            if filters.get("search"):
                search = f"%{filters['search']}%"
                query = query.join(User).filter(
                    or_(
                        Student.student_id.ilike(search),
                        User.full_name.ilike(search),
                        User.email.ilike(search),
                    )
                )
            if filters.get("department_id"):
                query = query.filter(Student.department_id == filters["department_id"])
            if filters.get("course"):
                query = query.filter(Student.course == filters["course"])
            if filters.get("semester"):
                query = query.filter(Student.semester == filters["semester"])
            if filters.get("status"):
                query = query.filter(Student.status == filters["status"])
        return query.order_by(Student.created_at.desc()).offset(skip).limit(limit).all()

    def get_count_with_filters(self, db: Session, filters: dict = None) -> int:
        query = db.query(Student)
        if filters:
            if filters.get("search"):
                search = f"%{filters['search']}%"
                query = query.join(User).filter(
                    or_(
                        Student.student_id.ilike(search),
                        User.full_name.ilike(search),
                        User.email.ilike(search),
                    )
                )
            if filters.get("department_id"):
                query = query.filter(Student.department_id == filters["department_id"])
            if filters.get("course"):
                query = query.filter(Student.course == filters["course"])
            if filters.get("semester"):
                query = query.filter(Student.semester == filters["semester"])
            if filters.get("status"):
                query = query.filter(Student.status == filters["status"])
        return query.count()

    def get_by_department(self, db: Session, department_id: int) -> List[Student]:
        return db.query(Student).filter(Student.department_id == department_id).all()

    def get_active_count(self, db: Session) -> int:
        return db.query(Student).filter(Student.status == UserStatus.ACTIVE).count()


crud_student = CRUDStudent(Student)