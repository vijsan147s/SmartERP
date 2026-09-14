import httpx
import random

c = httpx.Client(follow_redirects=True, timeout=15)
base = "http://localhost:8000/api/v1"

r = c.post(f"{base}/auth/login", json={"username": "admin", "password": "Admin@123"})
token = r.json()["tokens"]["access_token"]
h = {"Authorization": f"Bearer {token}"}

suffix = str(random.randint(100000, 999999))

print("--- CREATE STUDENT ---")
r = c.post(f"{base}/students/", headers=h, json={
    "student_id": f"STU{suffix}", "email": f"test{suffix}@smart.edu", "username": f"test{suffix}",
    "full_name": "Test Student", "phone": "9999999901", "department_id": 1,
    "course": "B.Tech", "semester": 1, "enrollment_date": "2024-08-15", "password": "Test@1234"
})
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:500]}")

print("\n--- CREATE EMPLOYEE ---")
r = c.post(f"{base}/employees/", headers=h, json={
    "employee_id": f"EMP{suffix}", "email": f"emptest{suffix}@smart.edu", "username": f"emptest{suffix}",
    "full_name": "Test Employee", "department_id": 1, "designation": "Professor",
    "joining_date": "2024-01-01", "salary": 75000, "password": "Test@1234"
})
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:500]}")

print("\n--- DASHBOARD REPORT ---")
r = c.get(f"{base}/reports/dashboard", headers=h)
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:800]}")

print("\n--- DEPARTMENTS REPORT ---")
r = c.get(f"{base}/reports/departments", headers=h)
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:500]}")

print("\n--- STUDENT LIST AS STUDENT ---")
r2 = c.post(f"{base}/auth/login", json={"username": "student", "password": "Student@123"})
sh = {"Authorization": f"Bearer {r2.json()['tokens']['access_token']}"}
r = c.get(f"{base}/students", headers=sh)
print(f"Status: {r.status_code}")
print(f"Body: {r.text[:500]}")

print("\n--- OPENAPI JSON ---")
r = c.get("http://localhost:8000/api/v1/openapi.json")
print(f"Status: {r.status_code}")
print(f"Content-Type: {r.headers.get('content-type', 'N/A')}")
print(f"Body length: {len(r.text)}")

c.close()
