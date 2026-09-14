from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from app.crud.base import CRUDBase
from app.models import Department, Employee, Student, UserStatus
from app.schemas.department import DepartmentCreate, DepartmentUpdate


class CRUDDepartment(CRUDBase[Department, DepartmentCreate, DepartmentUpdate]):
    def get_by_code(self, db: Session, code: str) -> Optional[Department]:
        return db.query(Department).filter(Department.code == code).first()

    def get_by_name(self, db: Session, name: str) -> Optional[Department]:
        return db.query(Department).filter(Department.name == name).first()

    def get_with_details(self, db: Session, id: int) -> Optional[Department]:
        return db.query(Department).options(
            joinedload(Department.head).joinedload(Employee.user),
            joinedload(Department.students),
            joinedload(Department.employees)
        ).filter(Department.id == id).first()

    def get_multi_with_counts(
        self, db: Session, *, skip: int = 0, limit: int = 100, filters: dict = None
    ) -> List[Department]:
        query = db.query(Department).options(
            joinedload(Department.head).joinedload(Employee.user)
        )
        if filters:
            if filters.get("search"):
                search = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Department.name.ilike(search),
                        Department.code.ilike(search),
                        Department.description.ilike(search),
                    )
                )
            if filters.get("status"):
                query = query.filter(Department.status == filters["status"])
        return query.order_by(Department.created_at.desc()).offset(skip).limit(limit).all()

    def get_count_with_filters(self, db: Session, filters: dict = None) -> int:
        query = db.query(Department)
        if filters:
            if filters.get("search"):
                search = f"%{filters['search']}%"
                query = query.filter(
                    or_(
                        Department.name.ilike(search),
                        Department.code.ilike(search),
                        Department.description.ilike(search),
                    )
                )
            if filters.get("status"):
                query = query.filter(Department.status == filters["status"])
        return query.count()

    def get_student_count(self, db: Session, department_id: int) -> int:
        return db.query(Student).filter(Student.department_id == department_id).count()

    def get_employee_count(self, db: Session, department_id: int) -> int:
        return db.query(Employee).filter(Employee.department_id == department_id).count()

    def get_all_active(self, db: Session) -> List[Department]:
        return db.query(Department).filter(Department.status == UserStatus.ACTIVE).all()


crud_department = CRUDDepartment(Department)