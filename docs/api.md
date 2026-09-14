# SmartERP API Documentation

**Base URL:** `http://localhost:8000/api/v1`

**Content-Type:** `application/json`

**Authentication:** Bearer JWT token in `Authorization` header

---

## Authentication

### Login

```
POST /api/v1/auth/login
```

**Auth Required:** No

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "email": "admin@smarterp.com",
    "username": "admin",
    "full_name": "Admin User",
    "phone": null,
    "avatar_url": null,
    "status": "ACTIVE",
    "is_superuser": true,
    "roles": ["ADMIN"],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00"
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "eyJ..."
  }
}
```

### Refresh Token

```
POST /api/v1/auth/refresh?refresh_token=<token>
```

**Auth Required:** No

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ..."
}
```

### Logout

```
POST /api/v1/auth/logout
```

**Auth Required:** Yes

**Response (200):**
```json
{ "message": "Successfully logged out" }
```

### Get Current User

```
GET /api/v1/auth/me
```

**Auth Required:** Yes (any role)

**Response (200):** `UserResponse`

### Change Password

```
POST /api/v1/auth/change-password
```

**Auth Required:** Yes (any role)

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response (200):**
```json
{ "message": "Password changed successfully" }
```

### Seed Roles

```
POST /api/v1/auth/seed-roles
```

**Auth Required:** Yes (ADMIN only)

**Response (200):**
```json
{ "message": "Roles seeded successfully" }
```

### Create Role

```
POST /api/v1/auth/roles
```

**Auth Required:** Yes (ADMIN only)

**Request Body:**
```json
{
  "name": "ADMIN|MANAGER|EMPLOYEE|STUDENT",
  "description": "string"
}
```

**Response (201):** `RoleResponse`

### Get All Roles

```
GET /api/v1/auth/roles
```

**Auth Required:** Yes (ADMIN only)

**Response (200):** `list[RoleResponse]`

---

## Students

### Create Student

```
POST /api/v1/students
```

**Auth Required:** Yes (MANAGER+)

**Request Body:**
```json
{
  "email": "string",
  "username": "string",
  "password": "string",
  "full_name": "string",
  "phone": "string",
  "student_id": "string",
  "department_id": 1,
  "course": "string",
  "semester": 1,
  "enrollment_date": "2024-08-15",
  "date_of_birth": "2000-01-01",
  "gender": "string",
  "address": "string",
  "emergency_contact": "string"
}
```

**Response (201):** `StudentResponse`

### Get Students (Paginated)

```
GET /api/v1/students
```

**Auth Required:** Yes (EMPLOYEE+)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | null | Search by name/email/student_id |
| `department_id` | int | null | Filter by department |
| `course` | string | null | Filter by course |
| `semester` | int | null | Filter by semester |
| `status` | string | null | Filter by status |
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |
| `sort_by` | string | created_at | Sort field |
| `sort_order` | string | desc | Sort direction |

**Response (200):** `PaginatedResponse` with `items: list[StudentListResponse]`

### Get Student by ID

```
GET /api/v1/students/{student_id}
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `StudentResponse`

### Update Student

```
PUT /api/v1/students/{student_id}
```

**Auth Required:** Yes (MANAGER+)

**Request Body:** Partial `StudentUpdate` schema

**Response (200):** `StudentResponse`

### Delete Student

```
DELETE /api/v1/students/{student_id}
```

**Auth Required:** Yes (ADMIN only)

**Response (200):**
```json
{ "message": "Student deleted successfully" }
```

### Get My Profile (Student)

```
GET /api/v1/students/me/profile
```

**Auth Required:** Yes (STUDENT)

**Response (200):** `StudentResponse`

---

## Employees

### Create Employee

```
POST /api/v1/employees
```

**Auth Required:** Yes (MANAGER+)

**Request Body:**
```json
{
  "email": "string",
  "username": "string",
  "password": "string",
  "full_name": "string",
  "phone": "string",
  "employee_id": "string",
  "department_id": 1,
  "designation": "string",
  "joining_date": "2024-01-01",
  "salary": 75000.00,
  "date_of_birth": "1990-01-01",
  "gender": "string",
  "address": "string",
  "emergency_contact": "string"
}
```

**Response (201):** `EmployeeResponse`

### Get Employees (Paginated)

```
GET /api/v1/employees
```

**Auth Required:** Yes (EMPLOYEE+)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | null | Search by name/email/employee_id |
| `department_id` | int | null | Filter by department |
| `designation` | string | null | Filter by designation |
| `status` | string | null | Filter by status |
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |

**Response (200):** `PaginatedResponse` with `items: list[EmployeeListResponse]`

### Get Employee by ID

```
GET /api/v1/employees/{employee_id}
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `EmployeeResponse`

### Update Employee

```
PUT /api/v1/employees/{employee_id}
```

**Auth Required:** Yes (MANAGER+)

**Request Body:** Partial `EmployeeUpdate` schema

**Response (200):** `EmployeeResponse`

### Delete Employee

```
DELETE /api/v1/employees/{employee_id}
```

**Auth Required:** Yes (ADMIN only)

**Response (200):**
```json
{ "message": "Employee deleted successfully" }
```

### Get My Profile (Employee)

```
GET /api/v1/employees/me/profile
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `EmployeeResponse`

---

## Departments

### Create Department

```
POST /api/v1/departments
```

**Auth Required:** Yes (ADMIN only)

**Request Body:**
```json
{
  "name": "string",
  "code": "string",
  "description": "string",
  "head_id": 1
}
```

**Response (201):** `DepartmentResponse`

### Get Departments (Paginated)

```
GET /api/v1/departments
```

**Auth Required:** Yes (EMPLOYEE+)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | null | Search by name/code |
| `status` | string | null | Filter by status |
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |

**Response (200):** `PaginatedResponse` with `items: list[DepartmentResponse]`

### Get All Active Departments

```
GET /api/v1/departments/all
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `list[DepartmentResponse]`

### Get Department by ID

```
GET /api/v1/departments/{department_id}
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `DepartmentResponse`

### Update Department

```
PUT /api/v1/departments/{department_id}
```

**Auth Required:** Yes (ADMIN only)

**Request Body:** Partial `DepartmentUpdate` schema

**Response (200):** `DepartmentResponse`

### Delete Department

```
DELETE /api/v1/departments/{department_id}
```

**Auth Required:** Yes (ADMIN only)

**Response (200):**
```json
{ "message": "Department deleted successfully" }
```

---

## Attendance

### Mark Attendance

```
POST /api/v1/attendance
```

**Auth Required:** Yes (MANAGER+)

**Request Body:**
```json
{
  "student_id": 1,
  "employee_id": null,
  "date": "2024-09-14",
  "status": "PRESENT|ABSENT|LATE|EXCUSED",
  "remarks": "string",
  "marked_by_id": 1
}
```

**Response (201):** `AttendanceResponse`

### Bulk Mark Attendance

```
POST /api/v1/attendance/bulk
```

**Auth Required:** Yes (MANAGER+)

**Request Body:**
```json
{
  "records": [
    { "student_id": 1, "date": "2024-09-14", "status": "PRESENT" },
    { "student_id": 2, "date": "2024-09-14", "status": "ABSENT" }
  ]
}
```

**Response (201):** `list[AttendanceResponse]`

### Get Attendance Records (Paginated)

```
GET /api/v1/attendance
```

**Auth Required:** Yes (EMPLOYEE+)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `student_id` | int | null | Filter by student |
| `employee_id` | int | null | Filter by employee |
| `department_id` | int | null | Filter by department |
| `date_from` | date | null | Start date filter |
| `date_to` | date | null | End date filter |
| `status` | string | null | Filter by status |
| `page` | int | 1 | Page number |
| `page_size` | int | 50 | Items per page (max 200) |

**Response (200):** `PaginatedResponse` with `items: list[AttendanceResponse]`

### Get Daily Attendance

```
GET /api/v1/attendance/daily?date=<date>&department_id=<int>
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `list[AttendanceResponse]`

### Get Student Attendance Stats

```
GET /api/v1/attendance/stats/student/{student_id}?date_from=<date>&date_to=<date>
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):**
```json
{
  "total_days": 30,
  "present_days": 25,
  "absent_days": 3,
  "late_days": 1,
  "excused_days": 1,
  "attendance_percentage": 83.33,
  "risk_level": "LOW"
}
```

### Get Employee Attendance Stats

```
GET /api/v1/attendance/stats/employee/{employee_id}?date_from=<date>&date_to=<date>
```

**Auth Required:** Yes (MANAGER+)

**Response (200):** `AttendanceStats`

### Get Monthly Attendance Report

```
GET /api/v1/attendance/report/monthly?department_id=<int>&year=<int>&month=<int>
```

**Auth Required:** Yes (MANAGER+)

**Response (200):** `MonthlyAttendanceReport`

### Get My Attendance Stats (Student)

```
GET /api/v1/attendance/me/stats
```

**Auth Required:** Yes (STUDENT)

**Response (200):** `AttendanceStats`

### Update Attendance

```
PUT /api/v1/attendance/{attendance_id}
```

**Auth Required:** Yes (MANAGER+)

**Request Body:** Partial `AttendanceUpdate` schema

**Response (200):** `AttendanceResponse`

### Delete Attendance

```
DELETE /api/v1/attendance/{attendance_id}
```

**Auth Required:** Yes (MANAGER+)

**Response (200):**
```json
{ "message": "Attendance deleted successfully" }
```

---

## Fees

### Create Fee

```
POST /api/v1/fees
```

**Auth Required:** Yes (MANAGER+)

**Request Body:**
```json
{
  "student_id": 1,
  "academic_year": "2024-2025",
  "semester": 1,
  "total_amount": 50000.00,
  "due_date": "2024-12-31",
  "remarks": "string"
}
```

**Response (201):** `FeeResponse`

### Get Fees (Paginated)

```
GET /api/v1/fees
```

**Auth Required:** Yes (EMPLOYEE+)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `student_id` | int | null | Filter by student |
| `department_id` | int | null | Filter by department |
| `academic_year` | string | null | Filter by year |
| `semester` | int | null | Filter by semester |
| `status` | string | null | Filter by status |
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |

**Response (200):** `PaginatedResponse` with `items: list[FeeListResponse]`

### Get Fee Dashboard Stats

```
GET /api/v1/fees/dashboard
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):**
```json
{
  "total_pending": 500000.00,
  "total_collected": 1200000.00,
  "paid_count": 45,
  "partial_count": 12,
  "pending_count": 8
}
```

### Get Fee by ID

```
GET /api/v1/fees/{fee_id}
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `FeeResponse`

### Update Fee

```
PUT /api/v1/fees/{fee_id}
```

**Auth Required:** Yes (MANAGER+)

**Request Body:** Partial `FeeUpdate` schema

**Response (200):** `FeeResponse`

### Create Payment

```
POST /api/v1/fees/{fee_id}/payments
```

**Auth Required:** Yes (MANAGER+)

**Request Body:**
```json
{
  "amount": 10000.00,
  "payment_date": "2024-09-14",
  "payment_method": "CASH|CARD|UPI|BANK_TRANSFER|CHEQUE|ONLINE",
  "transaction_id": "string",
  "receipt_number": "string",
  "remarks": "string"
}
```

**Response (201):** `PaymentResponse`

### Get Payments for Fee

```
GET /api/v1/fees/{fee_id}/payments
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `list[PaymentResponse]`

### Get My Fees (Student)

```
GET /api/v1/fees/me/fees
```

**Auth Required:** Yes (STUDENT)

**Response (200):** `list[FeeListResponse]`

### Delete Fee

```
DELETE /api/v1/fees/{fee_id}
```

**Auth Required:** Yes (MANAGER+)

**Response (200):**
```json
{ "message": "Fee deleted successfully" }
```

---

## Results

### Create Subject

```
POST /api/v1/results/subjects
```

**Auth Required:** Yes (ADMIN only)

**Request Body:**
```json
{
  "code": "CS101",
  "name": "Introduction to Programming",
  "department_id": 1,
  "credits": 3,
  "max_internal_marks": 30,
  "max_external_marks": 70,
  "semester": 1
}
```

**Response (201):** `SubjectResponse`

### Get Subjects (Paginated)

```
GET /api/v1/results/subjects
```

**Auth Required:** Yes (EMPLOYEE+)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `search` | string | null | Search by code/name |
| `department_id` | int | null | Filter by department |
| `semester` | int | null | Filter by semester |
| `is_active` | bool | null | Filter by active status |
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |

**Response (200):** `PaginatedResponse` with `items: list[SubjectResponse]`

### Get Subject by ID

```
GET /api/v1/results/subjects/{subject_id}
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `SubjectResponse`

### Update Subject

```
PUT /api/v1/results/subjects/{subject_id}
```

**Auth Required:** Yes (ADMIN only)

**Request Body:** Partial `SubjectUpdate` schema

**Response (200):** `SubjectResponse`

### Delete Subject

```
DELETE /api/v1/results/subjects/{subject_id}
```

**Auth Required:** Yes (ADMIN only)

**Response (200):**
```json
{ "message": "Subject deleted successfully" }
```

### Create Result

```
POST /api/v1/results
```

**Auth Required:** Yes (MANAGER+)

**Request Body:**
```json
{
  "student_id": 1,
  "subject_id": 1,
  "semester": 1,
  "internal_marks": 25,
  "external_marks": 60,
  "exam_date": "2024-09-14",
  "remarks": "string"
}
```

**Response (201):** `ResultResponse` (includes calculated `total_marks`, `grade`, `is_passed`)

### Get Results (Paginated)

```
GET /api/v1/results
```

**Auth Required:** Yes (EMPLOYEE+)

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `student_id` | int | null | Filter by student |
| `subject_id` | int | null | Filter by subject |
| `department_id` | int | null | Filter by department |
| `semester` | int | null | Filter by semester |
| `grade` | string | null | Filter by grade |
| `is_passed` | bool | null | Filter by pass status |
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Items per page (max 100) |

**Response (200):** `PaginatedResponse` with `items: list[ResultListResponse]`

### Get Result by ID

```
GET /api/v1/results/{result_id}
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `ResultResponse`

### Update Result

```
PUT /api/v1/results/{result_id}
```

**Auth Required:** Yes (MANAGER+)

**Request Body:** Partial `ResultUpdate` schema (re-calculates total/grade)

**Response (200):** `ResultResponse`

### Get Student Semester Results

```
GET /api/v1/results/student/{student_id}/semester/{semester}
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):** `StudentResultSummary`

### Get My Results (Student)

```
GET /api/v1/results/me/results?semester=<int>
```

**Auth Required:** Yes (STUDENT)

**Response (200):** `list[ResultListResponse]`

### Delete Result

```
DELETE /api/v1/results/{result_id}
```

**Auth Required:** Yes (MANAGER+)

**Response (200):**
```json
{ "message": "Result deleted successfully" }
```

---

## Reports

### Get Dashboard

```
GET /api/v1/reports/dashboard
```

**Auth Required:** Yes (EMPLOYEE+)

**Response (200):**
```json
{
  "stats": {
    "total_students": 120,
    "total_employees": 35,
    "attendance_rate": 87.5,
    "pending_fees": 250000.00,
    "total_departments": 8,
    "active_users": 155
  },
  "attendance_trend": [...],
  "department_distribution": [...],
  "fee_collection": [...],
  "fee_status": { "paid": 45, "partial": 12, "pending": 8 },
  "employee_student_distribution": { "employees": 35, "students": 120 }
}
```

### Student Report

```
GET /api/v1/reports/students?department_id=<int>&course=<str>&semester=<int>&status=<str>&export=<bool>
```

**Auth Required:** Yes (MANAGER+)

**Response (200):** `list[StudentReportRow]` (or CSV if `export=true`)

### Employee Report

```
GET /api/v1/reports/employees?department_id=<int>&designation=<str>&status=<str>&export=<bool>
```

**Auth Required:** Yes (MANAGER+)

**Response (200):** `list[EmployeeReportRow]` (or CSV if `export=true`)

### Attendance Report

```
GET /api/v1/reports/attendance?department_id=<int>&date_from=<date>&date_to=<date>&status=<str>&export=<bool>
```

**Auth Required:** Yes (MANAGER+)

**Response (200):** `list[AttendanceReportRow]` (or CSV if `export=true`)

### Fee Report

```
GET /api/v1/reports/fees?department_id=<int>&academic_year=<str>&semester=<int>&status=<str>&export=<bool>
```

**Auth Required:** Yes (MANAGER+)

**Response (200):** `list[FeeReportRow]` (or CSV if `export=true`)

### Department Report

```
GET /api/v1/reports/departments?status=<str>&export=<bool>
```

**Auth Required:** Yes (MANAGER+)

**Response (200):** `list[DepartmentReportRow]` (or CSV if `export=true`)

### Academic Performance Report

```
GET /api/v1/reports/academic-performance?department_id=<int>&course=<str>&semester=<int>&export=<bool>
```

**Auth Required:** Yes (MANAGER+)

**Response (200):** `list[AcademicPerformanceRow]` (or CSV if `export=true`)

---

## Common Response Formats

### Paginated Response

```json
{
  "items": [...],
  "total": 120,
  "page": 1,
  "page_size": 20,
  "total_pages": 6
}
```

### Error Response

```json
{
  "detail": "Error message"
}
```

### Standard HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient role) |
| 404 | Not Found |
| 409 | Conflict (duplicate entry) |
| 422 | Validation Error |
| 500 | Internal Server Error |
