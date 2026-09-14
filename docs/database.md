# SmartERP Database Documentation

## Overview

SmartERP uses **PostgreSQL** as its primary database with **SQLAlchemy ORM** for data access. The database contains **11 tables** covering users, roles, departments, students, employees, attendance, fees, payments, subjects, and results.

**Connection:** Configured via `DATABASE_URL` environment variable (default: `postgresql://postgres:postgres@localhost:5432/smatterp`)

---

## Tables

### 1. users

Stores all system user accounts (admins, managers, employees, students).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `email` | VARCHAR(255) | UNIQUE, INDEX, NOT NULL | User email address |
| `username` | VARCHAR(100) | UNIQUE, INDEX, NOT NULL | Login username |
| `hashed_password` | VARCHAR(255) | NOT NULL | Bcrypt-hashed password |
| `full_name` | VARCHAR(255) | NULLABLE | User's full name |
| `phone` | VARCHAR(20) | NULLABLE | Contact phone number |
| `avatar_url` | VARCHAR(500) | NULLABLE | Profile picture URL |
| `status` | ENUM(UserStatus) | NOT NULL, DEFAULT 'ACTIVE' | ACTIVE, INACTIVE, SUSPENDED |
| `last_login_at` | TIMESTAMP | NULLABLE | Timestamp of last login |
| `is_superuser` | BOOLEAN | NOT NULL, DEFAULT FALSE | Superuser flag (bypasses RBAC) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

### 2. roles

System roles for RBAC.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `name` | ENUM(UserRole) | UNIQUE, NOT NULL, INDEX | ADMIN, MANAGER, EMPLOYEE, STUDENT |
| `description` | VARCHAR(255) | NULLABLE | Role description |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether role is active |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

### 3. user_roles

Many-to-many relationship table between users and roles.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `user_id` | INTEGER | PK, FK → users.id (CASCADE) | User reference |
| `role_id` | INTEGER | PK, FK → roles.id (CASCADE) | Role reference |

**Constraints:** Composite primary key (user_id, role_id)

### 4. departments

Academic and organizational departments.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `name` | VARCHAR(100) | UNIQUE, NOT NULL, INDEX | Department name |
| `code` | VARCHAR(20) | UNIQUE, NOT NULL, INDEX | Short department code (e.g., "CS") |
| `description` | TEXT | NULLABLE | Department description |
| `head_id` | INTEGER | FK → employees.id (SET NULL), NULLABLE | Department head employee |
| `status` | ENUM(UserStatus) | NOT NULL, DEFAULT 'ACTIVE' | ACTIVE, INACTIVE, SUSPENDED |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

**Indexes:** `ix_departments_name_status` (name, status)

### 5. students

Student records linked to user accounts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `student_id` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Unique student identifier (e.g., "STU001") |
| `user_id` | INTEGER | FK → users.id (CASCADE), UNIQUE, NOT NULL | Linked user account |
| `department_id` | INTEGER | FK → departments.id (SET NULL), NULLABLE | Department enrollment |
| `course` | VARCHAR(100) | NOT NULL | Course name (e.g., "B.Tech") |
| `semester` | INTEGER | NOT NULL, DEFAULT 1 | Current semester |
| `enrollment_date` | DATE | NOT NULL | Date of enrollment |
| `date_of_birth` | DATE | NULLABLE | Student's date of birth |
| `gender` | VARCHAR(20) | NULLABLE | Gender |
| `address` | TEXT | NULLABLE | Residential address |
| `emergency_contact` | VARCHAR(255) | NULLABLE | Emergency contact info |
| `status` | ENUM(UserStatus) | NOT NULL, DEFAULT 'ACTIVE' | ACTIVE, INACTIVE, SUSPENDED |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

**Indexes:**
- `ix_students_dept_course_sem` (department_id, course, semester)
- `ix_students_status` (status)

### 6. employees

Employee records linked to user accounts.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `employee_id` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Unique employee identifier (e.g., "EMP001") |
| `user_id` | INTEGER | FK → users.id (CASCADE), UNIQUE, NOT NULL | Linked user account |
| `department_id` | INTEGER | FK → departments.id (SET NULL), NULLABLE | Department assignment |
| `designation` | VARCHAR(100) | NOT NULL | Job title/designation |
| `joining_date` | DATE | NOT NULL | Date of joining |
| `salary` | NUMERIC(12,2) | NOT NULL | Salary amount |
| `date_of_birth` | DATE | NULLABLE | Employee's date of birth |
| `gender` | VARCHAR(20) | NULLABLE | Gender |
| `address` | TEXT | NULLABLE | Residential address |
| `emergency_contact` | VARCHAR(255) | NULLABLE | Emergency contact info |
| `status` | ENUM(UserStatus) | NOT NULL, DEFAULT 'ACTIVE' | ACTIVE, INACTIVE, SUSPENDED |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

**Indexes:**
- `ix_employees_dept_designation` (department_id, designation)
- `ix_employees_status` (status)

### 7. attendance

Daily attendance records for students and employees.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `student_id` | INTEGER | FK → students.id (CASCADE), NULLABLE | Student reference |
| `employee_id` | INTEGER | FK → employees.id (CASCADE), NULLABLE | Employee reference |
| `date` | DATE | NOT NULL, INDEX | Attendance date |
| `status` | ENUM(AttendanceStatus) | NOT NULL | PRESENT, ABSENT, LATE, EXCUSED |
| `remarks` | TEXT | NULLABLE | Optional remarks |
| `marked_by_id` | INTEGER | FK → users.id (SET NULL), NULLABLE | Who marked the attendance |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

**Constraints:**
- `uq_student_date_attendance` — UNIQUE (student_id, date)
- `uq_employee_date_attendance` — UNIQUE (employee_id, date)

**Indexes:**
- `ix_attendance_student_date` (student_id, date)
- `ix_attendance_employee_date` (employee_id, date)
- `ix_attendance_date_status` (date, status)

### 8. fees

Student fee records per academic year/semester.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `student_id` | INTEGER | FK → students.id (CASCADE), NOT NULL, INDEX | Student reference |
| `academic_year` | VARCHAR(20) | NOT NULL | Academic year (e.g., "2024-2025") |
| `semester` | INTEGER | NOT NULL | Semester number |
| `total_amount` | NUMERIC(12,2) | NOT NULL | Total fee amount |
| `paid_amount` | NUMERIC(12,2) | NOT NULL, DEFAULT 0 | Amount paid so far |
| `pending_amount` | NUMERIC(12,2) | NOT NULL | Remaining balance |
| `due_date` | DATE | NULLABLE | Payment due date |
| `status` | ENUM(FeeStatus) | NOT NULL, DEFAULT 'PENDING' | PAID, PARTIAL, PENDING |
| `remarks` | TEXT | NULLABLE | Optional remarks |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

**Constraints:**
- `uq_student_year_sem_fee` — UNIQUE (student_id, academic_year, semester)

**Indexes:**
- `ix_fees_status` (status)
- `ix_fees_due_date` (due_date)

### 9. payments

Individual payment transactions linked to fee records.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `fee_id` | INTEGER | FK → fees.id (CASCADE), NOT NULL, INDEX | Fee record reference |
| `amount` | NUMERIC(12,2) | NOT NULL | Payment amount |
| `payment_date` | DATE | NOT NULL, INDEX | Date of payment |
| `payment_method` | ENUM(PaymentMethod) | NOT NULL | CASH, CARD, UPI, BANK_TRANSFER, CHEQUE, ONLINE |
| `transaction_id` | VARCHAR(100) | UNIQUE, NULLABLE | External transaction ID |
| `receipt_number` | VARCHAR(50) | UNIQUE, NOT NULL, INDEX | Receipt number |
| `remarks` | TEXT | NULLABLE | Optional remarks |
| `received_by_id` | INTEGER | FK → users.id (SET NULL), NULLABLE | User who received payment |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

**Indexes:** `ix_payments_fee_date` (fee_id, payment_date)

### 10. subjects

Academic subjects/courses.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `code` | VARCHAR(20) | UNIQUE, NOT NULL, INDEX | Subject code (e.g., "CS101") |
| `name` | VARCHAR(100) | NOT NULL | Subject name |
| `department_id` | INTEGER | FK → departments.id (SET NULL), NULLABLE | Department |
| `credits` | INTEGER | NOT NULL, DEFAULT 3 | Credit hours |
| `max_internal_marks` | INTEGER | NOT NULL, DEFAULT 30 | Maximum internal assessment marks |
| `max_external_marks` | INTEGER | NOT NULL, DEFAULT 70 | Maximum external exam marks |
| `semester` | INTEGER | NOT NULL | Semester for which subject is offered |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether subject is currently active |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

**Indexes:** `ix_subjects_dept_sem` (department_id, semester)

### 11. results

Student exam results linked to subjects.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PK, INDEX | Auto-incrementing primary key |
| `student_id` | INTEGER | FK → students.id (CASCADE), NOT NULL, INDEX | Student reference |
| `subject_id` | INTEGER | FK → subjects.id (CASCADE), NOT NULL, INDEX | Subject reference |
| `semester` | INTEGER | NOT NULL | Semester of the result |
| `internal_marks` | INTEGER | NOT NULL, DEFAULT 0 | Internal assessment marks |
| `external_marks` | INTEGER | NOT NULL, DEFAULT 0 | External exam marks |
| `total_marks` | INTEGER | NOT NULL, DEFAULT 0 | Computed total (internal + external) |
| `grade` | ENUM(Grade) | NULLABLE | A+, A, B+, B, C, F |
| `is_passed` | BOOLEAN | NOT NULL, DEFAULT FALSE | Auto-calculated pass/fail |
| `exam_date` | DATE | NULLABLE | Date of examination |
| `remarks` | TEXT | NULLABLE | Optional remarks |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record creation timestamp |
| `updated_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Record last update timestamp |

**Constraints:**
- `uq_student_subject_sem_result` — UNIQUE (student_id, subject_id, semester)

**Indexes:** `ix_results_student_sem` (student_id, semester)

---

## Entity Relationships

```
users ──1:1──> students          (user.id → student.user_id)
users ──1:1──> employees         (user.id → employee.user_id)
users ──M:N──> roles             (through user_roles junction table)
users ──1:N──> attendance        (marked_by_id)
users ──1:N──> payments          (received_by_id)

roles ──M:N──> users             (through user_roles junction table)

departments ──1:N──> students    (department.id → student.department_id)
departments ──1:N──> employees   (department.id → employee.department_id)
departments ──1:N──> subjects    (department.id → subject.department_id)
departments ──N:1──> employees   (department.head_id → employee.id)

students ──1:N──> attendance     (student.id → attendance.student_id)
students ──1:N──> fees           (student.id → fee.student_id)
students ──1:N──> results        (student.id → result.student_id)

employees ──1:N──> attendance    (employee.id → attendance.employee_id)

fees ──1:N──> payments           (fee.id → payment.fee_id)

subjects ──1:N──> results        (subject.id → result.subject_id)
```

---

## Grade Calculation Logic

The grade and pass/fail status are automatically calculated when creating or updating results:

| Total Marks (out of 100) | Grade | Pass? |
|---------------------------|-------|-------|
| ≥ 90 | A+ | Yes |
| ≥ 80 | A | Yes |
| ≥ 70 | B+ | Yes |
| ≥ 60 | B | Yes |
| ≥ 50 | C | Yes |
| < 50 | F | No |

**Calculation:**
```
total_marks = internal_marks + external_marks
grade = calculate_grade(total_marks, max_internal + max_external)
is_passed = (grade != "F")
```

---

## Fee Status Transitions

```
PENDING ──payment (partial)──> PARTIAL
PARTIAL ──payment (full)──> PAID
PENDING ──payment (full)──> PAID
```

**Rules:**
- `pending_amount = total_amount - paid_amount`
- `paid_amount` is incremented by each payment
- Status is recalculated on every payment and fee update

---

## Database Seeding

Roles are seeded automatically or via the `/api/v1/auth/seed-roles` endpoint (ADMIN only):

1. **ADMIN** — Full system access
2. **MANAGER** — Manage students, employees, attendance, fees, results
3. **EMPLOYEE** — Read-only access to most data
4. **STUDENT** — Self-service access only

A seed script in `backend/scripts/` creates the initial admin user and default departments.
