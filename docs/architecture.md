# SmartERP Architecture

## Overview

SmartERP is a full-stack Business & College Resource Management System built with a modern three-tier architecture separating presentation, business logic, and data persistence.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                         │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │              React + TypeScript + Vite + Tailwind          │  │
│  │                                                           │  │
│  │  Pages │ Components │ Hooks │ Store │ API Client (Axios)  │  │
│  └───────────────────────────┬───────────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────────┘
                               │  HTTP/HTTPS (REST API)
                               │  Content-Type: application/json
                               │  Authorization: Bearer <JWT>
┌──────────────────────────────┼──────────────────────────────────┐
│                        SERVER (Backend)                          │
│                              │                                   │
│  ┌───────────────────────────▼───────────────────────────────┐  │
│  │                   FastAPI Application                      │  │
│  │                                                           │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │  │
│  │  │   Routers    │  │ Dependencies │  │   Middleware    │  │  │
│  │  │  (API Views) │  │  (Auth, DB)  │  │   (CORS, JWT)  │  │  │
│  │  └──────┬──────┘  └──────┬───────┘  └────────────────┘  │  │
│  │         │                │                                │  │
│  │  ┌──────▼───────────────▼────────────────────────────┐   │  │
│  │  │              Pydantic Schemas                      │   │  │
│  │  │        (Validation, Serialization)                 │   │  │
│  │  └──────────────────────┬────────────────────────────┘   │  │
│  │                         │                                 │  │
│  │  ┌──────────────────────▼────────────────────────────┐   │  │
│  │  │                CRUD Layer                         │   │  │
│  │  │          (Business Logic, Queries)                 │   │  │
│  │  └──────────────────────┬────────────────────────────┘   │  │
│  │                         │                                 │  │
│  │  ┌──────────────────────▼────────────────────────────┐   │  │
│  │  │            SQLAlchemy ORM Models                  │   │  │
│  │  │         (User, Student, Employee, etc.)            │   │  │
│  │  └──────────────────────┬────────────────────────────┘   │  │
│  └─────────────────────────┼─────────────────────────────────┘  │
│                            │                                     │
│  ┌─────────────────────────▼─────────────────────────────────┐  │
│  │                     PostgreSQL                             │  │
│  │                                                           │  │
│  │  users │ roles │ user_roles │ departments │ students       │  │
│  │  employees │ attendance │ fees │ payments │ subjects       │  │
│  │  results                                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Frontend Layer (React + TypeScript + Vite + Tailwind)

**Technology Stack:**
- React 18 with TypeScript for type-safe UI development
- Vite as the build tool and dev server
- Tailwind CSS for utility-first styling
- React Router v6 for client-side routing
- Axios for HTTP requests
- React Hook Form + Zod for form validation
- TanStack React Query for server state management
- Recharts for data visualization
- Radix UI primitives for accessible components

**Responsibilities:**
- Render the user interface and handle user interactions
- Manage client-side routing (dashboard, students, employees, etc.)
- Send REST API requests to the backend via Axios
- Handle JWT token storage (access + refresh) and automatic token refresh
- Display paginated data, forms, and reports
- Client-side form validation using Zod schemas
- Display loading states, error messages, and success notifications

### 2. API Layer (FastAPI Routers)

**Located in:** `app/api/v1/`

**Responsibilities:**
- Define REST API endpoints for each domain module
- Accept and validate incoming requests using Pydantic schemas
- Enforce authentication via JWT token verification (`get_current_user` dependency)
- Enforce role-based access control via dependency injection (`require_admin`, `require_manager`, `require_employee`, `require_student`)
- Return properly formatted JSON responses with appropriate HTTP status codes
- Handle pagination, filtering, sorting, and search parameters

**Modules:**
| Router | Prefix | Tags |
|--------|--------|------|
| `auth.py` | `/api/v1/auth` | Authentication |
| `users.py` | `/api/v1/users` | Users |
| `students.py` | `/api/v1/students` | Students |
| `employees.py` | `/api/v1/employees` | Employees |
| `departments.py` | `/api/v1/departments` | Departments |
| `attendance.py` | `/api/v1/attendance` | Attendance |
| `fees.py` | `/api/v1/fees` | Fees |
| `results.py` | `/api/v1/results` | Results |
| `reports.py` | `/api/v1/reports` | Reports |

### 3. Business Logic Layer (CRUD Operations)

**Located in:** `app/crud/`

**Responsibilities:**
- Encapsulate all database queries and business rules
- Perform data validation beyond schema validation (e.g., uniqueness checks, constraint enforcement)
- Handle grade calculation logic (total marks, grade assignment, pass/fail determination)
- Manage fee payment tracking (paid_amount, pending_amount, status transitions)
- Provide reusable query methods with filtering, pagination, and eager loading
- Coordinate related entity creation (e.g., creating a User alongside a Student or Employee)

### 4. Data Access Layer (SQLAlchemy ORM)

**Located in:** `app/models/`

**Responsibilities:**
- Define database table schemas as Python classes
- Manage relationships between tables (one-to-many, many-to-many)
- Enforce constraints (unique, foreign key, not null)
- Handle database indexing for query performance
- Provide database-agnostic ORM abstraction over PostgreSQL
- Use `TimestampMixin` for automatic `created_at` / `updated_at` columns

### 5. Database Layer (PostgreSQL)

**Responsibilities:**
- Persistent storage for all application data
- Enforce data integrity through constraints, foreign keys, and unique indexes
- Support complex queries, aggregations, and joins for reports
- Transaction management for atomic multi-table operations
- JSON and enum support for structured data

## Authentication Flow

```
1. User submits credentials (username + password)
         │
         ▼
2. Backend verifies credentials against hashed_password
         │
         ▼
3. Backend generates JWT tokens:
   - access_token (expires in 30 minutes, contains user_id + roles)
   - refresh_token (expires in 7 days, contains user_id + roles)
         │
         ▼
4. Frontend stores tokens (memory/localStorage)
         │
         ▼
5. Subsequent requests include: Authorization: Bearer <access_token>
         │
         ▼
6. Backend decodes JWT, verifies expiry, checks user status
         │
         ▼
7. If access_token expired → use refresh_token to get new pair
```

## Role-Based Access Control (RBAC)

The system implements four distinct roles with escalating permissions:

| Role | Permissions |
|------|------------|
| **ADMIN** | Full system access. Manage all users, roles, departments, students, employees. Seed roles. Delete any record. |
| **MANAGER** | Create/update students, employees, attendance, fees, results. View all data. Generate reports. |
| **EMPLOYEE** | View students, employees, departments, attendance, fees, results. Limited to read operations. |
| **STUDENT** | View own profile, own attendance stats, own fees, own results. Self-service access only. |

RBAC is enforced at the API router level using FastAPI dependencies:
- `require_admin` — Only ADMIN role
- `require_manager` — MANAGER or ADMIN role
- `require_employee` — EMPLOYEE, MANAGER, or ADMIN role
- `require_student` — STUDENT role

## Exception Handling

The application registers global exception handlers in `app/main.py`:

- `AppException` → Custom application errors with structured responses
- `ValidationError` → Pydantic validation errors (422)
- `IntegrityError` → Database constraint violations (409/400)
- `HTTPException` → Standard HTTP errors (401, 403, 404, etc.)
- `Exception` → Unexpected errors (500)

## Data Flow Example: Creating a Student

```
1. Frontend sends POST /api/v1/students with student data
         │
         ▼
2. FastAPI validates request body against StudentCreate schema
         │
         ▼
3. require_manager dependency checks JWT + role
         │
         ▼
4. Router checks uniqueness (student_id, email)
         │
         ▼
5. Creates User object with hashed password
         │
         ▼
6. Assigns STUDENT role to user
         │
         ▼
7. Creates Student record linked to user
         │
         ▼
8. Commits to PostgreSQL in single transaction
         │
         ▼
9. Returns StudentResponse with full details
```
