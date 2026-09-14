from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from decimal import Decimal
from app.api.deps import get_db, require_manager, require_employee, require_student
from app.crud import crud_fee, crud_student, crud_payment
from app.schemas.fee import (
    FeeCreate, FeeUpdate, FeeResponse, FeeListResponse, FeeFilter,
    PaymentCreate, PaymentUpdate, PaymentResponse, FeeDashboardStats
)
from app.schemas.auth import PaginatedResponse
from app.models import FeeStatus, PaymentMethod, User

router = APIRouter()


@router.post("", response_model=FeeResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_manager)])
def create_fee(fee: FeeCreate, db: Session = Depends(get_db)):
    student = crud_student.get(db, fee.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    existing = crud_fee.get_by_student_year_sem(db, fee.student_id, fee.academic_year, fee.semester)
    if existing:
        raise HTTPException(status_code=409, detail="Fee record already exists for this student, year, and semester")
    
    fee_data = fee.model_dump()
    fee_data["pending_amount"] = fee.total_amount
    fee_data["paid_amount"] = Decimal("0")
    fee_data["status"] = FeeStatus.PENDING
    
    return crud_fee.create(db, obj_in=fee_data)


@router.get("", response_model=PaginatedResponse, dependencies=[Depends(require_employee)])
def get_fees(
    student_id: Optional[int] = None,
    department_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    semester: Optional[int] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    filters = {
        "student_id": student_id,
        "department_id": department_id,
        "academic_year": academic_year,
        "semester": semester,
        "status": status,
    }
    filters = {k: v for k, v in filters.items() if v is not None}
    
    fees = crud_fee.get_multi_with_details(db, skip=(page-1)*page_size, limit=page_size, filters=filters)
    total = crud_fee.get_count_with_filters(db, filters)
    
    items = []
    for f in fees:
        items.append(FeeListResponse(
            id=f.id,
            student_id=f.student_id,
            student_name=f.student.user.full_name,
            student_student_id=f.student.student_id,
            course=f.student.course,
            academic_year=f.academic_year,
            semester=f.semester,
            total_amount=f.total_amount,
            paid_amount=f.paid_amount,
            pending_amount=f.pending_amount,
            due_date=f.due_date,
            status=f.status,
            created_at=f.created_at,
        ))
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/dashboard", response_model=FeeDashboardStats, dependencies=[Depends(require_employee)])
def get_fee_dashboard(db: Session = Depends(get_db)):
    return crud_fee.get_dashboard_stats(db)


@router.get("/{fee_id}", response_model=FeeResponse, dependencies=[Depends(require_employee)])
def get_fee(fee_id: int, db: Session = Depends(get_db)):
    fee = crud_fee.get_with_details(db, fee_id)
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    return fee


@router.put("/{fee_id}", response_model=FeeResponse, dependencies=[Depends(require_manager)])
def update_fee(fee_id: int, fee_update: FeeUpdate, db: Session = Depends(get_db)):
    fee = crud_fee.get(db, fee_id)
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    
    update_data = fee_update.model_dump(exclude_unset=True)
    if "total_amount" in update_data:
        new_total = update_data["total_amount"]
        fee.pending_amount = new_total - fee.paid_amount
        if fee.pending_amount <= 0:
            fee.status = FeeStatus.PAID
        elif fee.paid_amount > 0:
            fee.status = FeeStatus.PARTIAL
        else:
            fee.status = FeeStatus.PENDING
    
    return crud_fee.update(db, db_obj=fee, obj_in=update_data)


@router.post("/{fee_id}/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_manager)])
def create_payment(fee_id: int, payment: PaymentCreate, db: Session = Depends(get_db)):
    fee = crud_fee.get(db, fee_id)
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    
    if crud_payment.get_by_receipt_number(db, payment.receipt_number):
        raise HTTPException(status_code=409, detail="Receipt number already exists")
    if payment.transaction_id and crud_payment.get_by_transaction_id(db, payment.transaction_id):
        raise HTTPException(status_code=409, detail="Transaction ID already exists")
    
    if payment.amount > fee.pending_amount:
        raise HTTPException(status_code=400, detail="Payment amount exceeds pending amount")
    
    payment_data = payment.model_dump()
    payment_data["fee_id"] = fee_id
    
    new_payment = crud_payment.create(db, obj_in=payment_data)
    
    fee.paid_amount += payment.amount
    fee.pending_amount = fee.total_amount - fee.paid_amount
    
    if fee.pending_amount <= 0:
        fee.status = FeeStatus.PAID
    elif fee.paid_amount > 0:
        fee.status = FeeStatus.PARTIAL
    else:
        fee.status = FeeStatus.PENDING
    
    db.commit()
    db.refresh(new_payment)
    
    return PaymentResponse.model_validate(new_payment)


@router.get("/{fee_id}/payments", response_model=List[PaymentResponse], dependencies=[Depends(require_employee)])
def get_payments(fee_id: int, db: Session = Depends(get_db)):
    fee = crud_fee.get(db, fee_id)
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    return crud_payment.get_by_fee_id(db, fee_id)


@router.get("/me/fees", response_model=List[FeeListResponse], dependencies=[Depends(require_student)])
def get_my_fees(current_user: User = Depends(require_student), db: Session = Depends(get_db)):
    student = crud_student.get_by_user_id(db, current_user.id)
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    
    fees = crud_fee.get_multi_with_details(db, filters={"student_id": student.id})
    return [
        FeeListResponse(
            id=f.id,
            student_id=f.student_id,
            student_name=f.student.user.full_name,
            student_student_id=f.student.student_id,
            course=f.student.course,
            academic_year=f.academic_year,
            semester=f.semester,
            total_amount=f.total_amount,
            paid_amount=f.paid_amount,
            pending_amount=f.pending_amount,
            due_date=f.due_date,
            status=f.status,
            created_at=f.created_at,
        )
        for f in fees
    ]


@router.delete("/{fee_id}", dependencies=[Depends(require_manager)])
def delete_fee(fee_id: int, db: Session = Depends(get_db)):
    fee = crud_fee.get(db, fee_id)
    if not fee:
        raise HTTPException(status_code=404, detail="Fee record not found")
    crud_fee.remove(db, id=fee_id)
    return {"message": "Fee deleted successfully"}