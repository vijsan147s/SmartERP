from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.models import User, Role, UserRole
from app.schemas.auth import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_by_email_or_username(self, db: Session, identifier: str) -> Optional[User]:
        return db.query(User).filter(
            or_(User.email == identifier, User.username == identifier)
        ).first()

    def get_multi_with_roles(
        self, db: Session, *, skip: int = 0, limit: int = 100, search: str = None, status: str = None
    ) -> List[User]:
        query = db.query(User)
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                )
            )
        if status:
            query = query.filter(User.status == status)
        return query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    def get_count_with_filters(self, db: Session, search: str = None, status: str = None) -> int:
        query = db.query(User)
        if search:
            query = query.filter(
                or_(
                    User.email.ilike(f"%{search}%"),
                    User.username.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%"),
                )
            )
        if status:
            query = query.filter(User.status == status)
        return query.count()

    def assign_roles(self, db: Session, user: User, roles: List[Role]) -> User:
        user.roles = roles
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def has_role(self, user: User, role_name: str) -> bool:
        return any(r.name == role_name for r in user.roles)

    def is_admin(self, user: User) -> bool:
        return self.has_role(user, UserRole.ADMIN) or user.is_superuser

    def is_manager(self, user: User) -> bool:
        return self.has_role(user, UserRole.MANAGER)

    def is_employee(self, user: User) -> bool:
        return self.has_role(user, UserRole.EMPLOYEE)

    def is_student(self, user: User) -> bool:
        return self.has_role(user, UserRole.STUDENT)


class CRUDRole(CRUDBase[Role, UserCreate, UserUpdate]):
    def get_by_name(self, db: Session, name: UserRole) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    def get_all_active(self, db: Session) -> List[Role]:
        return db.query(Role).filter(Role.is_active == True).all()


crud_user = CRUDUser(User)
crud_role = CRUDRole(Role)