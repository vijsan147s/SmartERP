from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from app.api.deps import get_db, require_manager, require_employee, require_student, require_admin
from app.crud import crud_result, crud_student, crud_subject
from app.schemas.result import (
    SubjectCreate, SubjectUpdate, SubjectResponse, SubjectFilter,
    ResultCreate, ResultUpdate, ResultResponse, ResultListResponse, ResultFilter,
    StudentResultSummary
)
from app.schemas.auth import PaginatedResponse
from app.models import User

router = APIRouter()


@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_subject(subject: SubjectCreate, db: Session = Depends(get_db)):
    if crud_subject.get_by_code(db, subject.code):
        raise HTTPException(status_code=409, detail="Subject code already exists")
    return crud_subject.create(db, obj_in=subject)


@router.get("/subjects", response_model=PaginatedResponse, dependencies=[Depends(require_employee)])
def get_subjects(
    search: Optional[str] = None,
    department_id: Optional[int] = None,
    semester: Optional[int] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "code",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    filters = {
        "search": search,
        "department_id": department_id,
        "semester": semester,
        "is_active": is_active,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    subjects = crud_subject.get_multi_with_department(db, skip=(page-1)*page_size, limit=page_size, filters=filters)
    total = db.query(crud_subject.model).count()
    
    items = [
        SubjectResponse.model_validate(s) for s in subjects
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/subjects/{subject_id}", response_model=SubjectResponse, dependencies=[Depends(require_employee)])
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = crud_subject.get_with_details(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject


@router.put("/subjects/{subject_id}", response_model=SubjectResponse, dependencies=[Depends(require_admin)])
def update_subject(subject_id: int, subject_update: SubjectUpdate, db: Session = Depends(get_db)):
    subject = crud_subject.get(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return crud_subject.update(db, db_obj=subject, obj_in=subject_update)


@router.post("", response_model=ResultResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_manager)])
def create_result(result: ResultCreate, db: Session = Depends(get_db)):
    student = crud_student.get(db, result.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    subject = crud_subject.get(db, result.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    if result.internal_marks > subject.max_internal_marks:
        raise HTTPException(status_code=400, detail=f"Internal marks cannot exceed {subject.max_internal_marks}")
    if result.external_marks > subject.max_external_marks:
        raise HTTPException(status_code=400, detail=f"External marks cannot exceed {subject.max_external_marks}")
    
    existing = crud_result.get_by_student_subject_sem(db, result.student_id, result.subject_id, result.semester)
    if existing:
        raise HTTPException(status_code=409, detail="Result already exists for this student, subject, and semester")
    
    calc = crud_result.calculate_total_and_grade(
        result.internal_marks, result.external_marks,
        subject.max_internal_marks, subject.max_external_marks
    )
    
    result_data = result.model_dump()
    result_data.update(calc)
    
    created = crud_result.create(db, obj_in=result_data)
    
    return ResultResponse(
        id=created.id,
        student_id=created.student_id,
        subject_id=created.subject_id,
        semester=created.semester,
        internal_marks=created.internal_marks,
        external_marks=created.external_marks,
        total_marks=created.total_marks,
        grade=created.grade,
        is_passed=created.is_passed,
        exam_date=created.exam_date,
        remarks=created.remarks,
        student_name=student.user.full_name,
        student_student_id=student.student_id,
        subject_name=subject.name,
        subject_code=subject.code,
        max_internal_marks=subject.max_internal_marks,
        max_external_marks=subject.max_external_marks,
        created_at=created.created_at,
        updated_at=created.updated_at,
    )


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_employee)])
def get_results(
    student_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    department_id: Optional[int] = None,
    semester: Optional[int] = None,
    grade: Optional[str] = None,
    is_passed: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    filters = {
        "student_id": student_id,
        "subject_id": subject_id,
        "department_id": department_id,
        "semester": semester,
        "grade": grade,
        "is_passed": is_passed,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    results = crud_result.get_multi_with_details(db, skip=(page-1)*page_size, limit=page_size, filters=filters)
    total = crud_result.get_count_with_filters(db, filters)
    
    items = []
    for r in results:
        items.append(ResultListResponse(
            id=r.id,
            student_id=r.student_id,
            student_name=r.student.user.full_name,
            student_student_id=r.student.student_id,
            subject_id=r.subject_id,
            subject_name=r.subject.name,
            subject_code=r.subject.code,
            semester=r.semester,
            internal_marks=r.internal_marks,
            external_marks=r.external_marks,
            total_marks=r.total_marks,
            grade=r.grade,
            is_passed=r.is_passed,
            created_at=r.created_at,
        ))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/{result_id}", response_model=ResultResponse, dependencies=[Depends(require_employee)])
def get_result(result_id: int, db: Session = Depends(get_db)):
    result = crud_result.get_with_details(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.put("/{result_id}", response_model=ResultResponse, dependencies=[Depends(require_manager)])
def update_result(result_id: int, result_update: ResultUpdate, db: Session = Depends(get_db)):
    result = crud_result.get(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    subject = crud_subject.get(db, result.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    update_data = result_update.model_dump(exclude_unset=True)
    internal = update_data.get("internal_marks", result.internal_marks)
    external = update_data.get("external_marks", result.external_marks)
    
    if internal > subject.max_internal_marks:
        raise HTTPException(status_code=400, detail=f"Internal marks cannot exceed {subject.max_internal_marks}")
    if external > subject.max_external_marks:
        raise HTTPException(status_code=400, detail=f"External marks cannot exceed {subject.max_external_marks}")
    
    calc = crud_result.calculate_total_and_grade(
        internal, external,
        subject.max_internal_marks, subject.max_external_marks
    )
    update_data.update(calc)
    
    return crud_result.update(db, db_obj=result, obj_in=update_data)


@router.get("/student/{student_id}/semester/{semester}", response_model=StudentResultSummary, dependencies=[Depends(require_employee)])
def get_student_semester_results(student_id: int, semester: int, db: Session = Depends(get_db)):
    student = crud_student.get(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud_result.get_student_summary(db, student_id, semester)


@router.get("/me/results", response_model=List[ResultListResponse], dependencies=[Depends(require_student)])
def get_my_results(
    semester: Optional[int] = None,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    student = crud_student.get_by_user_id(db, current_user.id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    filters = {"student_id": student.id}
    if semester:
        filters["semester"] = semester
    
    results = crud_result.get_multi_with_details(db, filters=filters, limit=100)
    return [
        ResultListResponse(
            id=r.id,
            student_id=r.student_id,
            student_name=r.student.user.full_name,
            student_student_id=r.student.student_id,
            subject_id=r.subject_id,
            subject_name=r.subject.name,
            subject_code=r.subject.code,
            semester=r.semester,
            internal_marks=r.internal_marks,
            external_marks=r.external_marks,
            total_marks=r.total_marks,
            grade=r.grade,
            is_passed=r.is_passed,
            created_at=r.created_at,
        )
        for r in results
    ]


@router.delete("/subjects/{subject_id}", dependencies=[Depends(require_admin)])
def delete_subject(subject_id: int, db: Session = Depends(get_db)):
    subject = crud_subject.get(db, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    crud_subject.remove(db, id=subject_id)
    return {"message": "Subject deleted successfully"}


@router.delete("/{result_id}", dependencies=[Depends(require_manager)])
def delete_result(result_id: int, db: Session = Depends(get_db)):
    result = crud_result.get(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    crud_result.remove(db, id=result_id)
    return {"message": "Result deleted successfully"}