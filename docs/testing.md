# SmartERP Testing Documentation

## Overview

SmartERP has **105 automated tests** covering authentication, CRUD operations, role-based access control, input validation, grade calculation, and reporting. Tests use pytest with an in-memory SQLite database for fast, isolated execution.

## Running Tests

```bash
# From the backend directory
cd backend

# Run all tests with verbose output
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test file
python -m pytest tests/test_auth.py -v

# Run a specific test
python -m pytest tests/test_students.py::test_create_student -v

# Run tests matching a keyword
python -m pytest tests/ -v -k "admin"
```

## Test Configuration

**Config file:** `backend/pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

**Dependencies:**
- pytest 8.2.2
- pytest-asyncio 0.23.3
- pytest-cov 5.0.0
- httpx 0.27.0 (for FastAPI TestClient)
- faker 25.2.0 (for generating test data)

---

## Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py            # Shared fixtures and helpers
├── test_auth.py           # Authentication tests
├── test_students.py       # Student CRUD tests
├── test_employees.py      # Employee CRUD tests
├── test_departments.py    # Department CRUD tests
├── test_attendance.py     # Attendance tests
├── test_fees.py           # Fee and payment tests
├── test_results.py        # Subject and result tests
└── test_reports.py        # Report generation tests
```

---

## conftest.py — Shared Fixtures

The `conftest.py` file provides reusable fixtures and helper functions used across all test modules.

### Database Setup

- Uses an in-memory SQLite database (`sqlite://`) with `StaticPool` for fast, isolated tests
- Each test creates all tables via `Base.metadata.create_all()` and drops them after completion
- `PRAGMA foreign_keys=ON` is enabled for proper FK enforcement in SQLite
- `get_db` dependency is overridden to use the test database session

### User Fixtures

| Fixture | Role | Credentials | Description |
|---------|------|-------------|-------------|
| `admin_user` | ADMIN | admin@smarterp.com / Admin@123 | Superuser admin account |
| `manager_user` | MANAGER | manager@smarterp.com / Manager@123 | Manager account |
| `employee_user` | EMPLOYEE | employee@smarterp.com / Employee@123 | Employee account |
| `student_user` | STUDENT | student@smarterp.com / Student@123 | Student account |

### Auth Header Fixtures

| Fixture | Description |
|---------|-------------|
| `admin_headers` | `{"Authorization": "Bearer <admin_token>"}` |
| `manager_headers` | `{"Authorization": "Bearer <manager_token>"}` |
| `employee_headers` | `{"Authorization": "Bearer <employee_token>"}` |
| `student_headers` | `{"Authorization": "Bearer <student_token>"}` |

### Other Fixtures

| Fixture | Description |
|---------|-------------|
| `roles` | Creates all 4 roles in the database |
| `department` | Creates a "Computer Science" department |
| `student` | Creates a test student linked to the department |
| `employee` | Creates a test employee linked to the department |
| `db` | Provides a test database session |
| `client` | Provides a FastAPI TestClient |

### Helper Functions

| Function | Description |
|----------|-------------|
| `create_roles(db)` | Seeds all 4 roles (ADMIN, MANAGER, EMPLOYEE, STUDENT) |
| `create_test_user(db, ...)` | Creates a user with a specific role |
| `create_test_student(db, ...)` | Creates a student record linked to a user |
| `create_test_employee(db, ...)` | Creates an employee record linked to a user |
| `create_test_department(db, ...)` | Creates a department |
| `get_auth_headers(user)` | Generates JWT auth headers for a user |

---

## Test Module Details

### test_auth.py — Authentication (15 tests)

Covers the complete authentication flow.

| Test | Description |
|------|-------------|
| `test_login_success` | Valid credentials return user + tokens |
| `test_login_invalid_credentials` | Wrong password returns 401 |
| `test_login_nonexistent_user` | Non-existent user returns 401 |
| `test_login_inactive_user` | Inactive user returns 403 |
| `test_get_current_user` | `/me` returns authenticated user |
| `test_get_current_user_no_token` | Missing token returns 401 |
| `test_change_password_success` | Valid current password allows change |
| `test_change_password_wrong_current` | Wrong current password returns 400 |
| `test_refresh_token` | Valid refresh token returns new token pair |
| `test_refresh_token_invalid` | Invalid refresh token returns 401 |
| `test_create_role_admin_only` | Non-admin gets 403 |
| `test_create_role_admin_success` | Admin can create roles |
| `test_create_role_duplicate` | Duplicate role returns 409 |
| `test_get_roles` | Admin can list roles |
| `test_seed_roles` | Admin can seed all roles |

### test_students.py — Student CRUD (14 tests)

Covers student creation, retrieval, update, deletion, and RBAC.

| Test | Description |
|------|-------------|
| `test_create_student_success` | Manager creates student with user account |
| `test_create_student_duplicate_student_id` | Duplicate student_id returns 409 |
| `test_create_student_duplicate_email` | Duplicate email returns 409 |
| `test_create_student_unauthorized` | Employee cannot create (403) |
| `test_get_students_list` | Paginated student list |
| `test_get_students_with_filters` | Filter by department/course/semester/status |
| `test_get_student_by_id` | Get single student |
| `test_get_student_not_found` | Non-existent ID returns 404 |
| `test_update_student_success` | Manager updates student |
| `test_update_student_email_conflict` | Email conflict returns 409 |
| `test_delete_student_admin_only` | Non-admin gets 403 |
| `test_delete_student_success` | Admin deletes student + user |
| `test_get_my_profile_student` | Student can view own profile |
| `test_student_profile_unauthorized` | Non-student cannot access /me/profile |

### test_employees.py — Employee CRUD (10 tests)

Covers employee creation, retrieval, update, deletion, and RBAC.

| Test | Description |
|------|-------------|
| `test_create_employee_success` | Manager creates employee |
| `test_create_employee_duplicate_id` | Duplicate employee_id returns 409 |
| `test_create_employee_duplicate_email` | Duplicate email returns 409 |
| `test_create_employee_unauthorized` | Employee role cannot create (403) |
| `test_get_employees_list` | Paginated employee list |
| `test_get_employee_by_id` | Get single employee |
| `test_get_employee_not_found` | Non-existent ID returns 404 |
| `test_update_employee_success` | Manager updates employee |
| `test_delete_employee_admin_only` | Non-admin gets 403 |
| `test_delete_employee_success` | Admin deletes employee + user |

### test_departments.py — Department CRUD (8 tests)

Covers department management and constraints.

| Test | Description |
|------|-------------|
| `test_create_department_success` | Admin creates department |
| `test_create_department_duplicate_code` | Duplicate code returns 409 |
| `test_create_department_duplicate_name` | Duplicate name returns 409 |
| `test_create_department_unauthorized` | Manager cannot create (403) |
| `test_get_departments_list` | Paginated department list |
| `test_get_department_by_id` | Get single department |
| `test_update_department_success` | Admin updates department |
| `test_delete_department_with_students` | Cannot delete dept with students (400) |

### test_attendance.py — Attendance (12 tests)

Covers attendance marking, stats, and reports.

| Test | Description |
|------|-------------|
| `test_mark_student_attendance` | Manager marks student present |
| `test_mark_employee_attendance` | Manager marks employee present |
| `test_mark_attendance_duplicate` | Same student+date returns 409 |
| `test_mark_attendance_no_entity` | Missing both IDs returns 400 |
| `test_mark_attendance_unauthorized` | Employee cannot mark (403) |
| `test_get_attendance_list` | Paginated attendance records |
| `test_get_daily_attendance` | Daily summary for a date |
| `test_get_student_attendance_stats` | Student attendance stats |
| `test_get_employee_attendance_stats` | Employee attendance stats |
| `test_update_attendance` | Manager updates attendance |
| `test_delete_attendance` | Manager deletes attendance |
| `test_get_monthly_report` | Monthly department report |

### test_fees.py — Fees & Payments (14 tests)

Covers fee creation, payment processing, and status tracking.

| Test | Description |
|------|-------------|
| `test_create_fee_success` | Manager creates fee record |
| `test_create_fee_duplicate` | Same student+year+semester returns 409 |
| `test_create_fee_student_not_found` | Non-existent student returns 404 |
| `test_get_fees_list` | Paginated fee list |
| `test_get_fee_by_id` | Get single fee |
| `test_update_fee_success` | Manager updates fee amount |
| `test_create_payment_success` | Manager creates payment, updates fee |
| `test_create_payment_exceeds_pending` | Payment > pending returns 400 |
| `test_create_payment_duplicate_receipt` | Duplicate receipt returns 409 |
| `test_create_payment_duplicate_transaction` | Duplicate transaction_id returns 409 |
| `test_get_payments_for_fee` | List payments for a fee |
| `test_fee_status_transitions` | PENDING → PARTIAL → PAID |
| `test_get_fee_dashboard` | Dashboard stats returned |
| `test_get_my_fees_student` | Student views own fees |

### test_results.py — Subjects & Results (20 tests)

Covers subject management, result creation, and grade calculation.

| Test | Description |
|------|-------------|
| `test_create_subject_success` | Admin creates subject |
| `test_create_subject_duplicate_code` | Duplicate code returns 409 |
| `test_create_subject_unauthorized` | Manager cannot create (403) |
| `test_get_subjects_list` | Paginated subject list |
| `test_get_subject_by_id` | Get single subject |
| `test_update_subject_success` | Admin updates subject |
| `test_delete_subject_success` | Admin deletes subject |
| `test_create_result_success` | Manager creates result with auto-calculation |
| `test_create_result_duplicate` | Same student+subject+semester returns 409 |
| `test_create_result_marks_exceed_max` | Marks > max returns 400 |
| `test_grade_calculation_a_plus` | 95/100 → A+ |
| `test_grade_calculation_a` | 85/100 → A |
| `test_grade_calculation_b_plus` | 75/100 → B+ |
| `test_grade_calculation_b` | 65/100 → B |
| `test_grade_calculation_c` | 55/100 → C |
| `test_grade_calculation_f` | 40/100 → F, is_passed=False |
| `test_update_result_recalculates` | Updating marks recalculates grade |
| `test_get_results_list` | Paginated result list |
| `test_get_student_semester_summary` | Semester summary with averages |
| `test_get_my_results_student` | Student views own results |

### test_reports.py — Reports (12 tests)

Covers dashboard and all report types.

| Test | Description |
|------|-------------|
| `test_get_dashboard` | Dashboard returns stats + trends |
| `test_get_dashboard_unauthorized` | Student cannot access (403) |
| `test_student_report` | Student report with attendance/fees |
| `test_student_report_csv_export` | CSV export format |
| `test_employee_report` | Employee report with attendance |
| `test_employee_report_csv_export` | CSV export format |
| `test_attendance_report` | Attendance report with filters |
| `test_attendance_report_csv_export` | CSV export format |
| `test_fee_report` | Fee report with payment info |
| `test_fee_report_csv_export` | CSV export format |
| `test_department_report` | Department stats report |
| `test_academic_performance_report` | Results with grades |

---

## Test Coverage Summary

| Module | Tests | Coverage Focus |
|--------|-------|----------------|
| Authentication | 15 | Login, JWT, RBAC, password change |
| Students | 14 | CRUD, duplicate checks, RBAC, profiles |
| Employees | 10 | CRUD, duplicate checks, RBAC |
| Departments | 8 | CRUD, uniqueness, FK constraints |
| Attendance | 12 | Mark, bulk, stats, daily, monthly |
| Fees | 14 | CRUD, payments, status transitions, dashboard |
| Results | 20 | Subjects, CRUD, grade calculation |
| Reports | 12 | Dashboard, all report types, CSV export |
| **Total** | **105** | |

## Testing Best Practices

1. **Isolation:** Each test runs with a fresh database (create/drop per function)
2. **No external dependencies:** Uses in-memory SQLite, no PostgreSQL required
3. **Role-based testing:** Each test uses appropriate auth headers for its role
4. **Edge cases:** Tests cover duplicate entries, unauthorized access, missing resources, and invalid data
5. **Grade calculation:** All 6 grade boundaries are explicitly tested
6. **Status transitions:** Fee payment status changes (PENDING → PARTIAL → PAID) are verified
