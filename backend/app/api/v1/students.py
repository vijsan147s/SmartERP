from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.api.deps import get_db, require_manager, require_employee, require_student, require_admin
from app.crud import crud_student, crud_user, crud_role
from app.schemas.student import (
    StudentCreate, StudentUpdate, StudentResponse, StudentListResponse, StudentFilter
)
from app.schemas.auth import PaginatedResponse
from app.models import User

router = APIRouter()


def _student_to_response(s) -> StudentResponse:
    return StudentResponse(
        id=s.id, student_id=s.student_id, user_id=s.user_id,
        email=s.user.email, username=s.user.username, full_name=s.user.full_name,
        phone=s.user.phone, department_id=s.department_id, course=s.course,
        semester=s.semester, enrollment_date=s.enrollment_date,
        date_of_birth=s.date_of_birth, gender=s.gender, address=s.address,
        emergency_contact=s.emergency_contact, status=s.status,
        created_at=s.created_at, updated_at=s.updated_at,
        department=s.department,
    )


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_manager)])
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    if crud_student.get_by_student_id(db, student.student_id):
        raise HTTPException(status_code=409, detail="Student ID already exists")
    
    existing_user = crud_user.get_by_email(db, student.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    
    from app.core.security import get_password_hash
    from app.models import User, UserRole
    
    user_data = {
        "email": student.email,
        "username": student.username,
        "full_name": student.full_name,
        "phone": student.phone,
        "hashed_password": get_password_hash(student.password),
        "status": "ACTIVE",
    }
    user_obj = User(**user_data)
    db.add(user_obj)
    db.flush()
    
    student_role = crud_role.get_by_name(db, UserRole.STUDENT)
    if student_role:
        user_obj.roles = [student_role]
    
    student_data = student.model_dump(exclude={"email", "username", "full_name", "phone", "password"})
    student_data["user_id"] = user_obj.id
    student_obj = crud_student.create(db, obj_in=student_data)
    
    s = crud_student.get_with_details(db, student_obj.id)
    return _student_to_response(s)


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_employee)])
def get_students(
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    course: Optional[str] = None,
    semester: Optional[int] = None,
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
        "course": course,
        "semester": semester,
        "status": status,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    students = crud_student.get_multi_with_details(db, skip=(page-1)*page_size, limit=page_size, filters=filters)
    total = crud_student.get_count_with_filters(db, filters)
    
    items = [
        StudentListResponse(
            id=s.id,
            student_id=s.student_id,
            full_name=s.user.full_name,
            email=s.user.email,
            phone=s.user.phone,
            department_name=s.department.name if s.department else None,
            course=s.course,
            semester=s.semester,
            enrollment_date=s.enrollment_date,
            status=s.status,
            created_at=s.created_at,
        )
        for s in students
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{student_id}", response_model=StudentResponse, dependencies=[Depends(require_employee)])
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud_student.get_with_details(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return _student_to_response(student)


@router.put("/{student_id}", response_model=StudentResponse, dependencies=[Depends(require_manager)])
def update_student(student_id: int, student_update: StudentUpdate, db: Session = Depends(get_db)):
    student = crud_student.get(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student_update.email and student_update.email != student.user.email:
        existing = crud_user.get_by_email(db, student_update.email)
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
    
    update_data = student_update.model_dump(exclude_unset=True)
    if "email" in update_data:
        student.user.email = update_data.pop("email")
    if "full_name" in update_data:
        student.user.full_name = update_data.pop("full_name")
    if "phone" in update_data:
        student.user.phone = update_data.pop("phone")
    
    for key, value in update_data.items():
        setattr(student, key, value)
    
    db.commit()
    db.refresh(student)
    s = crud_student.get_with_details(db, student_id)
    return _student_to_response(s)


@router.delete("/{student_id}", dependencies=[Depends(require_admin)])
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = crud_student.get(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    user_id = student.user_id
    crud_student.remove(db, id=student_id)
    
    from app.crud import crud_user
    crud_user.remove(db, id=user_id)
    
    return {"message": "Student deleted successfully"}


@router.get("/me/profile", response_model=StudentResponse, dependencies=[Depends(require_student)])
def get_my_profile(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = crud_student.get_by_user_id(db, current_user.id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return _student_to_response(crud_student.get_with_details(db, student.id))