from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, and_
from app.crud.base import CRUDBase
from app.models import Employee, User, Department, UserStatus
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


class CRUDEmployee(CRUDBase[Employee, EmployeeCreate, EmployeeUpdate]):
    def get_by_employee_id(self, db: Session, employee_id: str) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.employee_id == employee_id).first()

    def get_by_user_id(self, db: Session, user_id: int) -> Optional[Employee]:
        return db.query(Employee).filter(Employee.user_id == user_id).first()

    def get_with_details(self, db: Session, id: int) -> Optional[Employee]:
        return db.query(Employee).options(
            joinedload(Employee.user),
            joinedload(Employee.department)
        ).filter(Employee.id == id).first()

    def get_multi_with_details(
        self, db: Session, *, skip: int = 0, limit: int = 100, filters: dict = None
    ) -> List[Employee]:
        query = db.query(Employee).options(
            joinedload(Employee.user),
            joinedload(Employee.department)
        )
        if filters:
            if filters.get("search"):
                search = f"%{filters['search']}%"
                query = query.join(User).filter(
                    or_(
                        Employee.employee_id.ilike(search),
                        User.full_name.ilike(search),
                        User.email.ilike(search),
                    )
                )
            if filters.get("department_id"):
                query = query.filter(Employee.department_id == filters["department_id"])
            if filters.get("designation"):
                query = query.filter(Employee.designation == filters["designation"])
            if filters.get("status"):
                query = query.filter(Employee.status == filters["status"])
        return query.order_by(Employee.created_at.desc()).offset(skip).limit(limit).all()

    def get_count_with_filters(self, db: Session, filters: dict = None) -> int:
        query = db.query(Employee)
        if filters:
            if filters.get("search"):
                search = f"%{filters['search']}%"
                query = query.join(User).filter(
                    or_(
                        Employee.employee_id.ilike(search),
                        User.full_name.ilike(search),
                        User.email.ilike(search),
                    )
                )
            if filters.get("department_id"):
                query = query.filter(Employee.department_id == filters["department_id"])
            if filters.get("designation"):
                query = query.filter(Employee.designation == filters["designation"])
            if filters.get("status"):
                query = query.filter(Employee.status == filters["status"])
        return query.count()

    def get_by_department(self, db: Session, department_id: int) -> List[Employee]:
        return db.query(Employee).filter(Employee.department_id == department_id).all()

    def get_active_count(self, db: Session) -> int:
        return db.query(Employee).filter(Employee.status == UserStatus.ACTIVE).count()


crud_employee = CRUDEmployee(Employee)