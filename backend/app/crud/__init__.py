from app.crud.base import CRUDBase
from app.crud.user import crud_user, crud_role
from app.crud.student import crud_student
from app.crud.employee import crud_employee
from app.crud.department import crud_department
from app.crud.attendance import crud_attendance
from app.crud.fee import crud_fee, crud_payment
from app.crud.result import crud_subject, crud_result

__all__ = [
    "CRUDBase",
    "crud_user",
    "crud_role",
    "crud_student",
    "crud_employee",
    "crud_department",
    "crud_attendance",
    "crud_fee",
    "crud_payment",
    "crud_subject",
    "crud_result",
]