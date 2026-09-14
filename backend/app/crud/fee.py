from typing import Optional, List
from datetime import date
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, and_, extract
from app.crud.base import CRUDBase
from app.models import Fee, Payment, Student, FeeStatus, PaymentMethod
from app.schemas.fee import FeeCreate, FeeUpdate, PaymentCreate, PaymentUpdate


class CRUDFee(CRUDBase[Fee, FeeCreate, FeeUpdate]):
    def get_by_student_year_sem(
        self, db: Session, student_id: int, academic_year: str, semester: int
    ) -> Optional[Fee]:
        return db.query(Fee).filter(
            and_(
                Fee.student_id == student_id,
                Fee.academic_year == academic_year,
                Fee.semester == semester,
            )
        ).first()

    def get_with_details(self, db: Session, id: int) -> Optional[Fee]:
        return db.query(Fee).options(
            joinedload(Fee.student).joinedload(Student.user),
            joinedload(Fee.payments)
        ).filter(Fee.id == id).first()

    def get_multi_with_details(
        self, db: Session, *, skip: int = 0, limit: int = 100, filters: dict = None
    ) -> List[Fee]:
        query = db.query(Fee).options(
            joinedload(Fee.student).joinedload(Student.user),
            joinedload(Fee.student).joinedload(Student.department)
        )
        if filters:
            if filters.get("student_id"):
                query = query.filter(Fee.student_id == filters["student_id"])
            if filters.get("department_id"):
                query = query.join(Student).filter(Student.department_id == filters["department_id"])
            if filters.get("academic_year"):
                query = query.filter(Fee.academic_year == filters["academic_year"])
            if filters.get("semester"):
                query = query.filter(Fee.semester == filters["semester"])
            if filters.get("status"):
                query = query.filter(Fee.status == filters["status"])
        return query.order_by(Fee.created_at.desc()).offset(skip).limit(limit).all()

    def get_count_with_filters(self, db: Session, filters: dict = None) -> int:
        query = db.query(Fee)
        if filters:
            if filters.get("student_id"):
                query = query.filter(Fee.student_id == filters["student_id"])
            if filters.get("department_id"):
                query = query.join(Student).filter(Student.department_id == filters["department_id"])
            if filters.get("academic_year"):
                query = query.filter(Fee.academic_year == filters["academic_year"])
            if filters.get("semester"):
                query = query.filter(Fee.semester == filters["semester"])
            if filters.get("status"):
                query = query.filter(Fee.status == filters["status"])
        return query.count()

    def get_dashboard_stats(self, db: Session) -> dict:
        total_fees = db.query(func.sum(Fee.total_amount)).scalar() or Decimal("0")
        total_collected = db.query(func.sum(Fee.paid_amount)).scalar() or Decimal("0")
        total_pending = db.query(func.sum(Fee.pending_amount)).scalar() or Decimal("0")
        
        paid_count = db.query(Fee).filter(Fee.status == FeeStatus.PAID).count()
        partial_count = db.query(Fee).filter(Fee.status == FeeStatus.PARTIAL).count()
        pending_count = db.query(Fee).filter(Fee.status == FeeStatus.PENDING).count()
        
        collection_rate = float(total_collected / total_fees * 100) if total_fees > 0 else 0
        
        return {
            "total_fees": total_fees,
            "total_collected": total_collected,
            "total_pending": total_pending,
            "collection_rate": round(collection_rate, 2),
            "paid_count": paid_count,
            "partial_count": partial_count,
            "pending_count": pending_count,
        }

    def get_monthly_collection(self, db: Session, year: int) -> List[dict]:
        results = db.query(
            extract('month', Payment.payment_date).label('month'),
            func.sum(Payment.amount).label('collected')
        ).filter(
            extract('year', Payment.payment_date) == year
        ).group_by(extract('month', Payment.payment_date)).all()
        
        monthly = {int(r.month): float(r.collected) for r in results}
        return [
            {"month": f"{year}-{m:02d}", "collected": monthly.get(m, 0)}
            for m in range(1, 13)
        ]


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentUpdate]):
    def get_by_receipt_number(self, db: Session, receipt_number: str) -> Optional[Payment]:
        return db.query(Payment).filter(Payment.receipt_number == receipt_number).first()

    def get_by_transaction_id(self, db: Session, transaction_id: str) -> Optional[Payment]:
        return db.query(Payment).filter(Payment.transaction_id == transaction_id).first()

    def get_by_fee_id(self, db: Session, fee_id: int) -> List[Payment]:
        return db.query(Payment).filter(Payment.fee_id == fee_id).order_by(Payment.payment_date.desc()).all()


crud_fee = CRUDFee(Fee)
crud_payment = CRUDPayment(Payment)