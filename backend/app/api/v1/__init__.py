from fastapi import APIRouter
from app.api.v1 import auth, students, employees, departments, attendance, fees, results, reports, users

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
api_router.include_router(fees.router, prefix="/fees", tags=["Fees"])
api_router.include_router(results.router, prefix="/results", tags=["Results"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])