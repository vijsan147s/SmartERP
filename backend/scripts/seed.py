from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models import (
    User, Role, Department, Student, Employee, Subject, Attendance, Fee, Payment, Result,
    UserRole, UserStatus, AttendanceStatus, FeeStatus, PaymentMethod, Grade
)
from app.core.security import get_password_hash
from app.crud.result import crud_result
from datetime import date, timedelta
import random


def seed_roles(db: Session):
    for role_enum in UserRole:
        existing = db.query(Role).filter(Role.name == role_enum).first()
        if not existing:
            role = Role(name=role_enum, description=f"{role_enum.value} role", is_active=True)
            db.add(role)
    db.commit()


def seed_users(db: Session):
    users_data = [
        {
            "email": "admin@smart.edu",
            "username": "admin",
            "full_name": "System Administrator",
            "password": "Admin@123",
            "roles": [UserRole.ADMIN],
            "is_superuser": True,
        },
        {
            "email": "manager@smart.edu",
            "username": "manager",
            "full_name": "Department Manager",
            "password": "Manager@123",
            "roles": [UserRole.MANAGER],
        },
        {
            "email": "employee@smart.edu",
            "username": "employee",
            "full_name": "John Employee",
            "password": "Employee@123",
            "roles": [UserRole.EMPLOYEE],
        },
        {
            "email": "student@smart.edu",
            "username": "student",
            "full_name": "Jane Student",
            "password": "Student@123",
            "roles": [UserRole.STUDENT],
        },
    ]
    
    for user_data in users_data:
        roles = user_data.pop("roles")
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user_data["hashed_password"] = get_password_hash(user_data.pop("password"))
            user_data["status"] = UserStatus.ACTIVE
            user = User(**user_data)
            db.add(user)
            db.flush()
            
            role_objs = db.query(Role).filter(Role.name.in_(roles)).all()
            user.roles = role_objs
    
    db.commit()


def seed_departments(db: Session):
    departments_data = [
        {"name": "Computer Science", "code": "CS", "description": "Computer Science and Engineering Department"},
        {"name": "Information Technology", "code": "IT", "description": "Information Technology Department"},
        {"name": "Electronics", "code": "EC", "description": "Electronics and Communication Department"},
        {"name": "Mechanical", "code": "ME", "description": "Mechanical Engineering Department"},
        {"name": "Human Resources", "code": "HR", "description": "Human Resources Department"},
        {"name": "Finance", "code": "FN", "description": "Finance and Accounts Department"},
    ]
    
    for dept_data in departments_data:
        existing = db.query(Department).filter(Department.code == dept_data["code"]).first()
        if not existing:
            dept = Department(**dept_data, status=UserStatus.ACTIVE)
            db.add(dept)
    
    db.commit()


def seed_employees(db: Session):
    departments = db.query(Department).all()
    if not departments:
        return
    
    designations = ["Professor", "Associate Professor", "Assistant Professor", "Lecturer", "Lab Assistant", "Admin Staff"]
    
    for i in range(10):
        emp_id = f"EMP{1000 + i}"
        existing = db.query(Employee).filter(Employee.employee_id == emp_id).first()
        if existing:
            continue
        
        dept = random.choice(departments)
        user = User(
            email=f"emp{i+1}@smart.edu",
            username=f"emp{i+1}",
            full_name=f"Employee {i+1}",
            phone=f"98765432{i:02d}",
            hashed_password=get_password_hash("Employee@123"),
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        db.flush()
        
        emp_role = db.query(Role).filter(Role.name == UserRole.EMPLOYEE).first()
        if emp_role:
            user.roles = [emp_role]
        
        emp = Employee(
            employee_id=emp_id,
            user_id=user.id,
            department_id=dept.id,
            designation=random.choice(designations),
            joining_date=date(2020, 1, 1) + timedelta(days=random.randint(0, 1000)),
            salary=round(random.uniform(30000, 150000), 2),
            date_of_birth=date(1980, 1, 1) + timedelta(days=random.randint(0, 10000)),
            gender=random.choice(["Male", "Female"]),
            address=f"Address {i+1}, City",
            emergency_contact=f"98765432{i:02d}",
            status=UserStatus.ACTIVE,
        )
        db.add(emp)
    
    db.commit()


def seed_students(db: Session):
    departments = db.query(Department).all()
    if not departments:
        return
    
    courses = ["B.Tech", "M.Tech", "MBA", "MCA", "B.Sc", "M.Sc"]
    
    for i in range(30):
        student_id = f"STU{2000 + i}"
        existing = db.query(Student).filter(Student.student_id == student_id).first()
        if existing:
            continue
        
        dept = random.choice(departments)
        user = User(
            email=f"stu{i+1}@smart.edu",
            username=f"stu{i+1}",
            full_name=f"Student {i+1}",
            phone=f"87654321{i:02d}",
            hashed_password=get_password_hash("Student@123"),
            status=UserStatus.ACTIVE,
        )
        db.add(user)
        db.flush()
        
        stu_role = db.query(Role).filter(Role.name == UserRole.STUDENT).first()
        if stu_role:
            user.roles = [stu_role]
        
        course = random.choice(courses)
        semester = random.randint(1, 8) if "B" in course else random.randint(1, 4)
        
        stu = Student(
            student_id=student_id,
            user_id=user.id,
            department_id=dept.id,
            course=course,
            semester=semester,
            enrollment_date=date(2021, 7, 1) + timedelta(days=random.randint(0, 500)),
            date_of_birth=date(2000, 1, 1) + timedelta(days=random.randint(0, 2000)),
            gender=random.choice(["Male", "Female"]),
            address=f"Student Address {i+1}, City",
            emergency_contact=f"87654321{i:02d}",
            status=UserStatus.ACTIVE,
        )
        db.add(stu)
    
    db.commit()


def seed_subjects(db: Session):
    departments = db.query(Department).all()
    if not departments:
        return
    
    subjects_data = [
        ("CS101", "Programming Fundamentals", 3, 30, 70, 1),
        ("CS102", "Data Structures", 3, 30, 70, 2),
        ("CS103", "Algorithms", 4, 30, 70, 3),
        ("CS104", "Database Systems", 3, 30, 70, 4),
        ("CS105", "Operating Systems", 4, 30, 70, 5),
        ("CS106", "Computer Networks", 3, 30, 70, 6),
        ("IT101", "Web Technologies", 3, 30, 70, 1),
        ("IT102", "Software Engineering", 4, 30, 70, 2),
        ("IT103", "Cloud Computing", 3, 30, 70, 3),
        ("EC101", "Digital Electronics", 3, 30, 70, 1),
        ("EC102", "Microprocessors", 4, 30, 70, 2),
        ("ME101", "Thermodynamics", 3, 30, 70, 1),
        ("ME102", "Fluid Mechanics", 4, 30, 70, 2),
    ]
    
    for code, name, credits, max_int, max_ext, sem in subjects_data:
        existing = db.query(Subject).filter(Subject.code == code).first()
        if not existing:
            dept = next((d for d in departments if code.startswith(d.code[:2])), departments[0])
            subj = Subject(
                code=code,
                name=name,
                department_id=dept.id,
                credits=credits,
                max_internal_marks=max_int,
                max_external_marks=max_ext,
                semester=sem,
                is_active=True,
            )
            db.add(subj)
    
    db.commit()


def seed_fees(db: Session):
    students = db.query(Student).all()
    if not students:
        return
    
    for student in students:
        for year in ["2023-24", "2024-25"]:
            for sem in range(1, student.semester + 1):
                existing = db.query(Fee).filter(
                    Fee.student_id == student.id,
                    Fee.academic_year == year,
                    Fee.semester == sem,
                ).first()
                if existing:
                    continue
                
                total = round(random.uniform(50000, 150000), 2)
                paid = round(random.uniform(0, total), 2)
                
                fee = Fee(
                    student_id=student.id,
                    academic_year=year,
                    semester=sem,
                    total_amount=total,
                    paid_amount=paid,
                    pending_amount=total - paid,
                    due_date=date(2024, 6, 30) if sem % 2 == 0 else date(2024, 12, 31),
                    status=FeeStatus.PAID if paid >= total else (FeeStatus.PARTIAL if paid > 0 else FeeStatus.PENDING),
                    remarks=f"Semester {sem} fees",
                )
                db.add(fee)
                db.flush()
                
                if paid > 0:
                    payment = Payment(
                        fee_id=fee.id,
                        amount=paid,
                        payment_date=date.today() - timedelta(days=random.randint(1, 60)),
                        payment_method=random.choice(list(PaymentMethod)),
                        transaction_id=f"TXN{random.randint(100000, 999999)}",
                        receipt_number=f"RCP{random.randint(100000, 999999)}",
                        received_by_id=1,
                        remarks="Fee payment",
                    )
                    db.add(payment)
    
    db.commit()


def seed_attendance(db: Session):
    students = db.query(Student).all()
    employees = db.query(Employee).all()
    if not students and not employees:
        return
    
    for student in students[:20]:
        for day_offset in range(60):
            att_date = date.today() - timedelta(days=day_offset)
            if att_date.weekday() >= 5:
                continue
            
            existing = db.query(Attendance).filter(
                Attendance.student_id == student.id,
                Attendance.date == att_date,
            ).first()
            if existing:
                continue
            
            status = random.choices(
                [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.LATE, AttendanceStatus.EXCUSED],
                weights=[0.75, 0.15, 0.08, 0.02]
            )[0]
            
            attendance = Attendance(
                student_id=student.id,
                date=att_date,
                status=status,
                marked_by_id=1,
            )
            db.add(attendance)
    
    for employee in employees[:5]:
        for day_offset in range(60):
            att_date = date.today() - timedelta(days=day_offset)
            if att_date.weekday() >= 5:
                continue
            
            existing = db.query(Attendance).filter(
                Attendance.employee_id == employee.id,
                Attendance.date == att_date,
            ).first()
            if existing:
                continue
            
            status = random.choices(
                [AttendanceStatus.PRESENT, AttendanceStatus.ABSENT, AttendanceStatus.LATE],
                weights=[0.90, 0.05, 0.05]
            )[0]
            
            attendance = Attendance(
                employee_id=employee.id,
                date=att_date,
                status=status,
                marked_by_id=1,
            )
            db.add(attendance)
    
    db.commit()


def seed_results(db: Session):
    students = db.query(Student).all()
    subjects = db.query(Subject).filter(Subject.is_active == True).all()
    if not students or not subjects:
        return
    
    for student in students:
        student_subjects = [s for s in subjects if s.semester <= student.semester]
        for subject in student_subjects[:5]:
            existing = db.query(Result).filter(
                Result.student_id == student.id,
                Result.subject_id == subject.id,
                Result.semester == subject.semester,
            ).first()
            if existing:
                continue
            
            internal = random.randint(15, subject.max_internal_marks)
            external = random.randint(20, subject.max_external_marks)
            
            calc = crud_result.calculate_total_and_grade(
                internal, external,
                subject.max_internal_marks, subject.max_external_marks
            )
            
            result = Result(
                student_id=student.id,
                subject_id=subject.id,
                semester=subject.semester,
                internal_marks=internal,
                external_marks=external,
                total_marks=calc["total_marks"],
                grade=calc["grade"],
                is_passed=calc["is_passed"],
                exam_date=date.today() - timedelta(days=random.randint(1, 30)),
            )
            db.add(result)
    
    db.commit()


def run_seed():
    db = SessionLocal()
    try:
        print("Seeding roles...")
        seed_roles(db)
        
        print("Seeding users...")
        seed_users(db)
        
        print("Seeding departments...")
        seed_departments(db)
        
        print("Seeding employees...")
        seed_employees(db)
        
        print("Seeding students...")
        seed_students(db)
        
        print("Seeding subjects...")
        seed_subjects(db)
        
        print("Seeding fees...")
        seed_fees(db)
        
        print("Seeding attendance...")
        seed_attendance(db)
        
        print("Seeding results...")
        seed_results(db)
        
        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()