from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db, require_manager, require_employee, require_admin
from app.crud import crud_employee, crud_user, crud_role
from app.schemas.employee import (
    EmployeeCreate, EmployeeUpdate, EmployeeResponse, EmployeeListResponse, EmployeeFilter
)
from app.schemas.auth import PaginatedResponse
from app.models import User, UserRole
from app.core.security import get_password_hash

router = APIRouter()


def _employee_to_response(e) -> EmployeeResponse:
    return EmployeeResponse(
        id=e.id, employee_id=e.employee_id, user_id=e.user_id,
        email=e.user.email, username=e.user.username, full_name=e.user.full_name,
        phone=e.user.phone, department_id=e.department_id, designation=e.designation,
        joining_date=e.joining_date, salary=e.salary,
        date_of_birth=e.date_of_birth, gender=e.gender, address=e.address,
        emergency_contact=e.emergency_contact, status=e.status,
        created_at=e.created_at, updated_at=e.updated_at,
        department=e.department,
    )


@router.post("", response_model=EmployeeResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_manager)])
def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):
    if crud_employee.get_by_employee_id(db, employee.employee_id):
        raise HTTPException(status_code=409, detail="Employee ID already exists")
    
    user = crud_user.get_by_email(db, employee.email)
    if user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    user_data = {
        "email": employee.email,
        "username": employee.username,
        "full_name": employee.full_name,
        "phone": employee.phone,
        "hashed_password": get_password_hash(employee.password),
        "status": "ACTIVE",
    }
    user_obj = User(**user_data)
    db.add(user_obj)
    db.flush()
    
    employee_role = crud_role.get_by_name(db, UserRole.EMPLOYEE)
    if employee_role:
        user_obj.roles = [employee_role]
    
    employee_data = employee.model_dump(exclude={"email", "username", "full_name", "phone", "password"})
    employee_data["user_id"] = user_obj.id
    employee_obj = crud_employee.create(db, obj_in=employee_data)
    
    return _employee_to_response(crud_employee.get_with_details(db, employee_obj.id))


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_employee)])
def get_employees(
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    designation: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    filters = {
        "search": search,
        "department_id": department_id,
        "designation": designation,
        "status": status,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    employees = crud_employee.get_multi_with_details(db, skip=(page-1)*page_size, limit=page_size, filters=filters)
    total = crud_employee.get_count_with_filters(db, filters)
    
    items = [
        EmployeeListResponse(
            id=e.id,
            employee_id=e.employee_id,
            full_name=e.user.full_name,
            email=e.user.email,
            phone=e.user.phone,
            department_name=e.department.name if e.department else None,
            designation=e.designation,
            joining_date=e.joining_date,
            salary=e.salary,
            status=e.status,
            created_at=e.created_at,
        )
        for e in employees
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{employee_id}", response_model=EmployeeResponse, dependencies=[Depends(require_employee)])
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = crud_employee.get_with_details(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return _employee_to_response(employee)


@router.put("/{employee_id}", response_model=EmployeeResponse, dependencies=[Depends(require_manager)])
def update_employee(employee_id: int, employee_update: EmployeeUpdate, db: Session = Depends(get_db)):
    employee = crud_employee.get(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if employee_update.email and employee_update.email != employee.user.email:
        existing = crud_user.get_by_email(db, employee_update.email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
    
    update_data = employee_update.model_dump(exclude_unset=True)
    if "email" in update_data:
        employee.user.email = update_data.pop("email")
    if "full_name" in update_data:
        employee.user.full_name = update_data.pop("full_name")
    if "phone" in update_data:
        employee.user.phone = update_data.pop("phone")
    
    for key, value in update_data.items():
        setattr(employee, key, value)
    
    db.commit()
    db.refresh(employee)
    return _employee_to_response(crud_employee.get_with_details(db, employee_id))


@router.delete("/{employee_id}", dependencies=[Depends(require_admin)])
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    employee = crud_employee.get(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    user_id = employee.user_id
    crud_employee.remove(db, id=employee_id)
    crud_user.remove(db, id=user_id)
    
    return {"message": "Employee deleted successfully"}


@router.get("/me/profile", response_model=EmployeeResponse, dependencies=[Depends(require_employee)])
def get_my_profile(current_user: User = Depends(require_employee), db: Session = Depends(get_db)):
    employee = crud_employee.get_by_user_id(db, current_user.id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee profile not found")
    return _employee_to_response(crud_employee.get_with_details(db, employee.id))