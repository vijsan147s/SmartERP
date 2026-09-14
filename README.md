# SmartERP

### Smart Business & College Resource Management System

A full-stack ERP application built with React, TypeScript, FastAPI, SQLAlchemy, and PostgreSQL. Demonstrates real-world software engineering skills including authentication, role-based authorization, CRUD operations, dashboard analytics, and comprehensive testing.

## Features

- **Authentication & Authorization** - JWT-based auth with 4 roles (Admin, Manager, Employee, Student)
- **Student Management** - Full CRUD with search, filter, sort, and pagination
- **Employee Management** - Department assignment, designation tracking, salary management
- **Department Management** - Code/name uniqueness, head assignment, student/employee counts
- **Attendance System** - Daily marking, bulk operations, statistics with risk level calculation
- **Fee Management** - Payment processing, collection tracking, dashboard statistics
- **Academic Results** - Subject management, automatic grade calculation (A+ to F)
- **Reports & Analytics** - Dashboard charts, CSV export, departmental reports
- **Professional UI** - Responsive sidebar layout, toast notifications, confirmation dialogs

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Radix UI |
| Backend | Python 3, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL |
| Auth | JWT (access + refresh tokens), bcrypt |
| Testing | Pytest, FastAPI TestClient |

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Node.js 18+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# Seed database
python scripts/seed.py

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

### Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | Admin@123 |
| Manager | manager | Manager@123 |
| Employee | employee | Employee@123 |
| Student | student | Student@123 |

## Environment Variables

```env
DATABASE_URL=postgresql://user:password@localhost:5432/smarterp
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=["http://localhost:5173"]
ENVIRONMENT=development
```

## Testing

```bash
cd backend

# Run all tests
python -m pytest tests/ -v

# Run specific module
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_students.py -v
```

**105 tests** across 8 modules covering authentication, CRUD operations, RBAC, validation, grade calculation, and reports.

## API Documentation

Once the server is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Import `postman/SmartERP.postman_collection.json` into Postman for the complete API collection.

## Project Structure

```
SmartERP/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API route handlers
│   │   ├── core/            # Config, database, security
│   │   ├── crud/            # Database operations
│   │   ├── models/          # SQLAlchemy models
│   │   └── schemas/         # Pydantic schemas
│   ├── scripts/             # Database seed script
│   ├── tests/               # Pytest test suite (105 tests)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service layer
│   │   ├── context/         # Auth context
│   │   └── types/           # TypeScript interfaces
│   └── package.json
├── docs/                    # Project documentation
├── postman/                 # API collection
└── README.md
```

## Database Schema

10 normalized tables with proper relationships:

- **users** & **roles** (many-to-many via user_roles)
- **departments** - Head assignment, status tracking
- **students** & **employees** - User-linked profiles with department assignment
- **attendance** - Daily tracking with PRESENT/ABSENT/LATE/EXCUSED statuses
- **fees** & **payments** - Financial tracking with PAID/PARTIAL/PENDING statuses
- **subjects** & **results** - Academic performance with automatic grade calculation

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, layers, data flow |
| [Database](docs/database.md) | Schema, relationships, constraints |
| [API](docs/api.md) | All endpoints with request/response details |
| [Testing](docs/testing.md) | Test structure, coverage, running tests |
| [Setup](docs/setup.md) | Installation and configuration guide |

## License

This project is for educational purposes.

## Author

Built as a demonstration of full-stack software engineering skills for ERP development.
