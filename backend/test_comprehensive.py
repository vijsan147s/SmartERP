import httpx
import json
import sys
import random

base = "http://localhost:8000/api/v1"
c = httpx.Client(follow_redirects=True, timeout=15)
errors = []
suffix = str(random.randint(100000, 999999))

def test(name, fn):
    try:
        result = fn()
        if result is False:
            errors.append(name)
            print(f"  FAIL: {name}")
        else:
            print(f"  PASS: {name}")
    except Exception as e:
        errors.append(name)
        print(f"  FAIL: {name} -> {e}")

print("\n=== 1. HEALTH CHECK ===")
test("GET /health", lambda: c.get("http://localhost:8000/health").status_code == 200)
test("GET /", lambda: c.get("http://localhost:8000/").status_code == 200)

print("\n=== 2. AUTH - ADMIN LOGIN ===")
r = c.post(f"{base}/auth/login", json={"username": "admin", "password": "Admin@123"})
test("Admin login 200", lambda: r.status_code == 200)
admin_token = r.json()["tokens"]["access_token"] if r.status_code == 200 else None
admin_headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else {}

test("Login returns user", lambda: "full_name" in r.json().get("user", {}))
test("Login returns tokens", lambda: "access_token" in r.json().get("tokens", {}))

test("GET /auth/me", lambda: c.get(f"{base}/auth/me", headers=admin_headers).status_code == 200)
test("/auth/me returns admin name", lambda: c.get(f"{base}/auth/me", headers=admin_headers).json()["full_name"] == "System Administrator")

print("\n=== 3. AUTH - MANAGER LOGIN ===")
r = c.post(f"{base}/auth/login", json={"username": "manager", "password": "Manager@123"})
test("Manager login 200", lambda: r.status_code == 200)
mgr_token = r.json()["tokens"]["access_token"] if r.status_code == 200 else None
mgr_headers = {"Authorization": f"Bearer {mgr_token}"} if mgr_token else {}

print("\n=== 4. AUTH - EMPLOYEE LOGIN ===")
r = c.post(f"{base}/auth/login", json={"username": "employee", "password": "Employee@123"})
test("Employee login 200", lambda: r.status_code == 200)
emp_token = r.json()["tokens"]["access_token"] if r.status_code == 200 else None
emp_headers = {"Authorization": f"Bearer {emp_token}"} if emp_token else {}

print("\n=== 5. AUTH - STUDENT LOGIN ===")
r = c.post(f"{base}/auth/login", json={"username": "student", "password": "Student@123"})
test("Student login 200", lambda: r.status_code == 200)
stu_token = r.json()["tokens"]["access_token"] if r.status_code == 200 else None
stu_headers = {"Authorization": f"Bearer {stu_token}"} if stu_token else {}

print("\n=== 6. AUTH - INVALID CREDENTIALS ===")
test("Wrong password 401", lambda: c.post(f"{base}/auth/login", json={"username": "admin", "password": "wrong"}).status_code == 401)
test("Empty login 422", lambda: c.post(f"{base}/auth/login", json={}).status_code == 422)
test("No token 401/403", lambda: c.get(f"{base}/auth/me").status_code in [401, 403])

print("\n=== 7. STUDENTS CRUD (ADMIN) ===")
# Create
r = c.post(f"{base}/students/", headers=admin_headers, json={
    "student_id": f"STU{suffix}", "email": f"test{suffix}@smart.edu", "username": f"test{suffix}",
    "full_name": "Test Student One", "phone": "9999999901", "department_id": 1,
    "course": "B.Tech", "semester": 1, "enrollment_date": "2024-08-15", "password": "Test@1234"
})
test("Create student 200/201", lambda: r.status_code in [200, 201])
created_id = r.json().get("id") if r.status_code in [200, 201] else None

# Read
r = c.get(f"{base}/students", headers=admin_headers)
test("List students 200", lambda: r.status_code == 200)
test("Students list has items", lambda: len(r.json().get("items", [])) > 0)

if created_id:
    r = c.get(f"{base}/students/{created_id}", headers=admin_headers)
    test("Get student by id 200", lambda: r.status_code == 200)

    # Update
    r = c.put(f"{base}/students/{created_id}", headers=admin_headers, json={"full_name": "Updated Student"})
    test("Update student 200", lambda: r.status_code == 200)

    # Delete
    r = c.delete(f"{base}/students/{created_id}", headers=admin_headers)
    test("Delete student 200", lambda: r.status_code == 200)

# Duplicate - use seed data student_id which still exists
r = c.post(f"{base}/students/", headers=admin_headers, json={
    "student_id": "STU001", "email": f"dup{suffix}@smart.edu", "username": f"dup{suffix}",
    "full_name": "Dup", "course": "B.Tech", "semester": 1,
    "enrollment_date": "2024-08-15", "password": "Test@1234"
})
test("Duplicate student_id 409", lambda: r.status_code == 409)

print("\n=== 8. EMPLOYEES CRUD (ADMIN) ===")
r = c.post(f"{base}/employees/", headers=admin_headers, json={
    "employee_id": f"EMP{suffix}", "email": f"emptest{suffix}@smart.edu", "username": f"emptest{suffix}",
    "full_name": "Test Employee", "department_id": 1, "designation": "Professor",
    "joining_date": "2024-01-01", "salary": 75000, "password": "Test@1234"
})
test("Create employee 200/201", lambda: r.status_code in [200, 201])
emp_created_id = r.json().get("id") if r.status_code in [200, 201] else None

r = c.get(f"{base}/employees", headers=admin_headers)
test("List employees 200", lambda: r.status_code == 200)
test("Employees list has items", lambda: len(r.json().get("items", [])) > 0)

if emp_created_id:
    r = c.get(f"{base}/employees/{emp_created_id}", headers=admin_headers)
    test("Get employee by id 200", lambda: r.status_code == 200)
    r = c.delete(f"{base}/employees/{emp_created_id}", headers=admin_headers)
    test("Delete employee 200", lambda: r.status_code == 200)

print("\n=== 9. DEPARTMENTS CRUD (ADMIN) ===")
r = c.post(f"{base}/departments/", headers=admin_headers, json={
    "name": "Test Department", "code": "TD", "description": "Test Dept"
})
test("Create department 200/201", lambda: r.status_code in [200, 201])
dept_id = r.json().get("id") if r.status_code in [200, 201] else None

r = c.get(f"{base}/departments", headers=admin_headers)
test("List departments 200", lambda: r.status_code == 200)
test("Departments list has items", lambda: len(r.json().get("items", [])) > 0)

if dept_id:
    r = c.get(f"{base}/departments/{dept_id}", headers=admin_headers)
    test("Get department by id 200", lambda: r.status_code == 200)
    r = c.put(f"{base}/departments/{dept_id}", headers=admin_headers, json={"description": "Updated"})
    test("Update department 200", lambda: r.status_code == 200)
    r = c.delete(f"{base}/departments/{dept_id}", headers=admin_headers)
    test("Delete department 200", lambda: r.status_code == 200)

print("\n=== 10. ATTENDANCE ===")
r = c.post(f"{base}/attendance/", headers=admin_headers, json={
    "student_id": 3, "date": f"2024-{random.randint(10,12):02d}-{random.randint(1,28):02d}", "status": "PRESENT", "remarks": "Test"
})
test("Create attendance 200/201", lambda: r.status_code in [200, 201])
att_id = r.json().get("id") if r.status_code in [200, 201] else None

r = c.get(f"{base}/attendance", headers=admin_headers)
test("List attendance 200", lambda: r.status_code == 200)

r = c.get(f"{base}/attendance/stats/student/1", headers=admin_headers)
test("Student attendance stats 200", lambda: r.status_code == 200)

if att_id:
    r = c.put(f"{base}/attendance/{att_id}", headers=admin_headers, json={"status": "ABSENT"})
    test("Update attendance 200", lambda: r.status_code == 200)

print("\n=== 11. FEES ===")
r = c.get(f"{base}/fees", headers=admin_headers)
test("List fees 200", lambda: r.status_code == 200)

r = c.get(f"{base}/fees/dashboard", headers=admin_headers)
test("Fees dashboard 200", lambda: r.status_code == 200)

print("\n=== 12. RESULTS ===")
r = c.get(f"{base}/results", headers=admin_headers)
test("List results 200", lambda: r.status_code == 200)

r = c.get(f"{base}/results/subjects", headers=admin_headers)
test("List subjects 200", lambda: r.status_code == 200)

print("\n=== 13. REPORTS (ADMIN) ===")
r = c.get(f"{base}/reports/dashboard", headers=admin_headers)
test("Dashboard report 200", lambda: r.status_code == 200)

r = c.get(f"{base}/reports/students", headers=admin_headers)
test("Students report 200", lambda: r.status_code == 200)

r = c.get(f"{base}/reports/employees", headers=admin_headers)
test("Employees report 200", lambda: r.status_code == 200)

r = c.get(f"{base}/reports/attendance", headers=admin_headers)
test("Attendance report 200", lambda: r.status_code == 200)

r = c.get(f"{base}/reports/fees", headers=admin_headers)
test("Fees report 200", lambda: r.status_code == 200)

r = c.get(f"{base}/reports/departments", headers=admin_headers)
test("Departments report 200", lambda: r.status_code == 200)

r = c.get(f"{base}/reports/academic-performance", headers=admin_headers)
test("Academic report 200", lambda: r.status_code == 200)

print("\n=== 14. ROLE-BASED ACCESS ===")
# Student shouldn't access student management
r = c.get(f"{base}/students", headers=stu_headers)
test("Student cannot list students (403)", lambda: r.status_code == 403)

r = c.post(f"{base}/students/", headers=stu_headers, json={
    "student_id": "STU_X", "email": "x@x.com", "username": "x",
    "full_name": "X", "course": "X", "semester": 1,
    "enrollment_date": "2024-01-01", "password": "Test@1234"
})
test("Student cannot create student (403)", lambda: r.status_code == 403)

# Employee shouldn't access fee creation
r = c.post(f"{base}/fees/", headers=emp_headers, json={
    "student_id": 1, "academic_year": "2024-25", "semester": 1,
    "total_amount": 50000, "due_date": "2024-12-31"
})
test("Employee cannot create fee (403)", lambda: r.status_code == 403)

print("\n=== 15. PAGINATION ===")
r = c.get(f"{base}/students?page=1&page_size=5", headers=admin_headers)
test("Students pagination page_size=5", lambda: r.status_code == 200 and len(r.json().get("items", [])) <= 5)

r = c.get(f"{base}/employees?page=1&page_size=3", headers=admin_headers)
test("Employees pagination page_size=3", lambda: r.status_code == 200 and len(r.json().get("items", [])) <= 3)

print("\n=== 16. SEARCH/FILTER ===")
r = c.get(f"{base}/students?search=Student", headers=admin_headers)
test("Students search works", lambda: r.status_code == 200)

r = c.get(f"{base}/employees?search=Employee", headers=admin_headers)
test("Employees search works", lambda: r.status_code == 200)

print("\n=== 17. CSV EXPORT ===")
r = c.get(f"{base}/reports/students?format=csv", headers=admin_headers)
test("Students CSV export", lambda: r.status_code == 200)

r = c.get(f"{base}/reports/attendance?format=csv", headers=admin_headers)
test("Attendance CSV export", lambda: r.status_code == 200)

print("\n=== 18. TOKEN REFRESH ===")
refresh_token = None
r = c.post(f"{base}/auth/login", json={"username": "admin", "password": "Admin@123"})
if r.status_code == 200:
    refresh_token = r.json()["tokens"]["refresh_token"]
if refresh_token:
    r = c.post(f"{base}/auth/refresh", params={"refresh_token": refresh_token})
    test("Token refresh 200", lambda: r.status_code == 200)
    test("New access token returned", lambda: "access_token" in r.json())

print("\n=== 19. OPENAPI DOCS ===")
r = c.get("http://localhost:8000/docs")
test("Swagger UI accessible", lambda: r.status_code == 200)
r = c.get("http://localhost:8000/api/v1/openapi.json")
test("OpenAPI JSON available", lambda: r.status_code == 200)

print(f"\n{'='*50}")
print(f"RESULTS: {len(errors)} FAILURES")
if errors:
    print(f"Failed tests:")
    for e in errors:
        print(f"  - {e}")
print(f"{'='*50}")

c.close()
sys.exit(1 if errors else 0)
