import os
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only-12345678"
os.environ["ENVIRONMENT"] = "test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.core.security import get_password_hash, create_access_token
from app.models import User, Role, UserRole, UserStatus, Department, Student, Employee


SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def _drop_all_tables():
    with engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys = OFF"))
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(text(f"DROP TABLE IF EXISTS {table.name}"))
        conn.execute(text("PRAGMA foreign_keys = ON"))
        conn.commit()


@pytest.fixture(autouse=True, scope="function")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    _drop_all_tables()


@pytest.fixture(autouse=True)
def setup_overrides():
    from app.api.deps import get_db as deps_get_db
    from app.main import app
    app.dependency_overrides[deps_get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    from app.main import app
    from app.api.deps import get_db as deps_get_db
    app.dependency_overrides[deps_get_db] = override_get_db
    with TestClient(app) as c:
        yield c


def create_roles(db):
    roles = {}
    for role in UserRole:
        existing = db.query(Role).filter(Role.name == role).first()
        if not existing:
            r = Role(name=role, description=f"{role.value} role")
            db.add(r)
            db.flush()
            roles[role] = r
        else:
            roles[role] = existing
    db.commit()
    return roles


def create_test_user(db, username, email, full_name, password, role, is_superuser=False):
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=get_password_hash(password),
        status=UserStatus.ACTIVE,
        is_superuser=is_superuser,
    )
    db.add(user)
    db.flush()
    role_obj = db.query(Role).filter(Role.name == role).first()
    if role_obj:
        user.roles = [role_obj]
    db.commit()
    db.refresh(user)
    return user


def create_test_department(db, name="Computer Science", code="CS"):
    dept = Department(name=name, code=code, description=f"{name} Department")
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


def create_test_student(db, user, department_id=None, student_id="STU001"):
    from datetime import date
    student = Student(
        student_id=student_id,
        user_id=user.id,
        department_id=department_id,
        course="B.Tech",
        semester=1,
        enrollment_date=date(2024, 8, 15),
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def create_test_employee(db, user, department_id=None, employee_id="EMP001"):
    from decimal import Decimal
    from datetime import date
    employee = Employee(
        employee_id=employee_id,
        user_id=user.id,
        department_id=department_id,
        designation="Professor",
        joining_date=date(2024, 1, 1),
        salary=Decimal("75000.00"),
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def get_auth_headers(user):
    token = create_access_token(
        data={"sub": str(user.id), "roles": [r.name.value for r in user.roles]}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def roles(db):
    return create_roles(db)


@pytest.fixture
def admin_user(db, roles):
    return create_test_user(db, "admin", "admin@smarterp.com", "Admin User", "Admin@123", UserRole.ADMIN, is_superuser=True)


@pytest.fixture
def manager_user(db, roles):
    return create_test_user(db, "manager", "manager@smarterp.com", "Manager User", "Manager@123", UserRole.MANAGER)


@pytest.fixture
def employee_user(db, roles):
    return create_test_user(db, "employee", "employee@smarterp.com", "Employee User", "Employee@123", UserRole.EMPLOYEE)


@pytest.fixture
def student_user(db, roles):
    return create_test_user(db, "student", "student@smarterp.com", "Student User", "Student@123", UserRole.STUDENT)


@pytest.fixture
def admin_headers(admin_user):
    return get_auth_headers(admin_user)


@pytest.fixture
def manager_headers(manager_user):
    return get_auth_headers(manager_user)


@pytest.fixture
def employee_headers(employee_user):
    return get_auth_headers(employee_user)


@pytest.fixture
def student_headers(student_user):
    return get_auth_headers(student_user)


@pytest.fixture
def department(db):
    return create_test_department(db)


@pytest.fixture
def student(db, department):
    user = create_test_user(db, "teststudent", "test@student.com", "Test Student", "Student@123", UserRole.STUDENT)
    return create_test_student(db, user, department.id, "STU001")


@pytest.fixture
def employee(db, department):
    user = create_test_user(db, "testemployee", "test@employee.com", "Test Employee", "Employee@123", UserRole.EMPLOYEE)
    return create_test_employee(db, user, department.id, "EMP001")
