# SmartERP Setup Guide

## Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.10+ | Backend runtime |
| PostgreSQL | 12+ | Database |
| Node.js | 18+ | Frontend runtime |
| npm | 8+ | Frontend package manager |

## Project Structure

```
SmartERP/
├── backend/                # FastAPI Python backend
│   ├── app/                # Application source code
│   │   ├── api/            # API routes and dependencies
│   │   ├── core/           # Config, database, security
│   │   ├── crud/           # Database operations
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # FastAPI app entry point
│   ├── tests/              # Test suite
│   ├── scripts/            # Seed scripts
│   ├── migrations/         # Alembic migrations
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
├── frontend/               # React TypeScript frontend
│   ├── src/                # Source code
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite configuration
├── postman/                # API collection
└── docs/                   # Documentation
```

---

## Backend Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Key packages:**
| Package | Version | Purpose |
|---------|---------|---------|
| fastapi | 0.111.0 | Web framework |
| uvicorn | 0.30.1 | ASGI server |
| sqlalchemy | 2.0.30 | ORM |
| alembic | 1.13.1 | Database migrations |
| psycopg2-binary | 2.9.9 | PostgreSQL driver |
| pydantic | 2.7.4 | Data validation |
| python-jose | 3.3.0 | JWT tokens |
| passlib | 1.7.4 | Password hashing |
| httpx | 0.27.0 | Test client |
| pytest | 8.2.2 | Test framework |

### 3. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/smatterp

# Security
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:5173", "http://127.0.0.1:5173"]

# Environment
ENVIRONMENT=development
```

### 4. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE smatterp;

# Exit
\q
```

### 5. Seed Initial Data

```bash
# Seed roles (ADMIN, MANAGER, EMPLOYEE, STUDENT)
python scripts/seed.py
```

Or use the API after starting the server:
```bash
# Login as admin, then call:
curl -X POST http://localhost:8000/api/v1/auth/seed-roles \
  -H "Authorization: Bearer <admin_token>"
```

### 6. Run Server

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/api/v1/openapi.json

---

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

**Key packages:**
| Package | Version | Purpose |
|---------|---------|---------|
| react | 18.2.0 | UI framework |
| react-router-dom | 6.22.0 | Client-side routing |
| axios | 1.6.7 | HTTP client |
| react-hook-form | 7.51.0 | Form management |
| zod | 3.22.4 | Schema validation |
| recharts | 2.12.0 | Charts |
| @tanstack/react-query | 5.24.0 | Server state |
| tailwindcss | 3.4.1 | CSS framework |
| lucide-react | 0.344.0 | Icons |

### 2. Run Development Server

```bash
npm run dev
```

Frontend available at: http://localhost:5173

### 3. Build for Production

```bash
npm run build
npm run preview
```

---

## Environment Variables Reference

### Backend (.env)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | — | PostgreSQL connection string |
| `SECRET_KEY` | Yes | — | JWT signing key (min 32 chars) |
| `ALGORITHM` | No | HS256 | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | 30 | Access token TTL |
| `REFRESH_TOKEN_EXPIRE_DAYS` | No | 7 | Refresh token TTL |
| `CORS_ORIGINS` | No | localhost:5173 | Allowed CORS origins |
| `ENVIRONMENT` | No | development | Environment mode |

### Database URL Format

```
postgresql://<username>:<password>@<host>:<port>/<database_name>
```

Examples:
```
# Local
postgresql://postgres:postgres@localhost:5432/smatterp

# Remote
postgresql://user:pass@db.example.com:5432/smatterp

# With SSL
postgresql://user:pass@host:5432/db?sslmode=require
```

---

## Testing

### Run All Tests

```bash
cd backend
python -m pytest tests/ -v
```

### Run with Coverage

```bash
python -m pytest tests/ -v --cov=app --cov-report=term-missing
```

### Run Specific Module

```bash
python -m pytest tests/test_auth.py -v
python -m pytest tests/test_students.py -v
python -m pytest tests/test_employees.py -v
python -m pytest tests/test_departments.py -v
python -m pytest tests/test_attendance.py -v
python -m pytest tests/test_fees.py -v
python -m pytest tests/test_results.py -v
python -m pytest tests/test_reports.py -v
```

**Note:** Tests use an in-memory SQLite database — no PostgreSQL required for testing.

---

## Troubleshooting

### Common Issues

**1. Database connection error**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
- Ensure PostgreSQL is running
- Check `DATABASE_URL` in `.env`
- Verify database `smatterp` exists

**2. Port already in use**
```
[Errno 10048] Only one usage of each socket address is permitted
```
- Kill existing process: `lsof -i :8000` (macOS/Linux) or `netstat -ano | findstr :8000` (Windows)
- Or use a different port: `uvicorn app.main:app --port 8001`

**3. Module not found**
```
ModuleNotFoundError: No module named 'app'
```
- Ensure you're in the `backend/` directory
- Ensure virtual environment is activated

**4. JWT errors**
```
jwt.exceptions.InvalidTokenError
```
- Ensure `SECRET_KEY` is set and at least 32 characters
- Ensure token is not expired (default 30 min)

**5. Frontend API errors**
- Ensure backend is running on port 8000
- Check `CORS_ORIGINS` includes `http://localhost:5173`
- Verify API base URL in frontend config

---

## Default Credentials

After seeding, use these credentials for testing:

| Role | Email | Password |
|------|-------|----------|
| ADMIN | admin@smarterp.com | Admin@123 |
| MANAGER | manager@smarterp.com | Manager@123 |
| EMPLOYEE | employee@smarterp.com | Employee@123 |
| STUDENT | student@smarterp.com | Student@123 |

**Note:** These are created by test fixtures. For production, seed via the `/api/v1/auth/seed-roles` endpoint and create users through the admin panel.
