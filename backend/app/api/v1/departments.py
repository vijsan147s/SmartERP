from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db, require_manager, require_admin, require_employee
from app.crud import crud_department
from app.schemas.department import (
    DepartmentCreate, DepartmentUpdate, DepartmentResponse, DepartmentFilter
)
from app.schemas.auth import PaginatedResponse

router = APIRouter()


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    if crud_department.get_by_code(db, department.code):
        raise HTTPException(status_code=409, detail="Department code already exists")
    if crud_department.get_by_name(db, department.name):
        raise HTTPException(status_code=409, detail="Department name already exists")
    return crud_department.create(db, obj_in=department)


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_employee)])
def get_departments(
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    filters = {"search": search, "status": status}
    filters = {k: v for k, v in filters.items() if v is not None}
    
    departments = crud_department.get_multi_with_counts(db, skip=(page-1)*page_size, limit=page_size, filters=filters)
    total = crud_department.get_count_with_filters(db, filters)
    
    items = []
    for d in departments:
        student_count = crud_department.get_student_count(db, d.id)
        employee_count = crud_department.get_employee_count(db, d.id)
        head_name = d.head.user.full_name if d.head and d.head.user else None
        
        items.append(DepartmentResponse(
            id=d.id,
            name=d.name,
            code=d.code,
            description=d.description,
            head_id=d.head_id,
            status=d.status,
            created_at=d.created_at,
            updated_at=d.updated_at,
            head_name=head_name,
            student_count=student_count,
            employee_count=employee_count,
        ))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/all", response_model=list[DepartmentResponse], dependencies=[Depends(require_employee)])
def get_all_departments(db: Session = Depends(get_db)):
    departments = crud_department.get_all_active(db)
    return [
        DepartmentResponse(
            id=d.id,
            name=d.name,
            code=d.code,
            description=d.description,
            head_id=d.head_id,
            status=d.status,
            created_at=d.created_at,
            updated_at=d.updated_at,
            student_count=crud_department.get_student_count(db, d.id),
            employee_count=crud_department.get_employee_count(db, d.id),
        )
        for d in departments
    ]


@router.get("/{department_id}", response_model=DepartmentResponse, dependencies=[Depends(require_employee)])
def get_department(department_id: int, db: Session = Depends(get_db)):
    department = crud_department.get_with_details(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    student_count = crud_department.get_student_count(db, department.id)
    employee_count = crud_department.get_employee_count(db, department.id)
    head_name = department.head.user.full_name if department.head and department.head.user else None
    
    return DepartmentResponse(
        id=department.id,
        name=department.name,
        code=department.code,
        description=department.description,
        head_id=department.head_id,
        status=department.status,
        created_at=department.created_at,
        updated_at=department.updated_at,
        head_name=head_name,
        student_count=student_count,
        employee_count=employee_count,
    )


@router.put("/{department_id}", response_model=DepartmentResponse, dependencies=[Depends(require_admin)])
def update_department(department_id: int, department_update: DepartmentUpdate, db: Session = Depends(get_db)):
    department = crud_department.get(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    update_data = department_update.model_dump(exclude_unset=True)
    if "code" in update_data and update_data["code"] != department.code:
        if crud_department.get_by_code(db, update_data["code"]):
            raise HTTPException(status_code=409, detail="Department code already exists")
    if "name" in update_data and update_data["name"] != department.name:
        if crud_department.get_by_name(db, update_data["name"]):
            raise HTTPException(status_code=409, detail="Department name already exists")
    
    for key, value in update_data.items():
        setattr(department, key, value)
    
    db.commit()
    db.refresh(department)
    return get_department(department_id, db)


@router.delete("/{department_id}", dependencies=[Depends(require_admin)])
def delete_department(department_id: int, db: Session = Depends(get_db)):
    department = crud_department.get(db, department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    if crud_department.get_student_count(db, department_id) > 0:
        raise HTTPException(status_code=400, detail="Cannot delete department with students")
    if crud_department.get_employee_count(db, department_id) > 0:
        raise HTTPException(status_code=400, detail="Cannot delete department with employees")
    
    crud_department.remove(db, id=department_id)
    return {"message": "Department deleted successfully"}