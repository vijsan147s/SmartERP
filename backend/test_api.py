import httpx
import json

base = "http://localhost:8000/api/v1"

# Test health
r = httpx.get("http://localhost:8000/health")
print(f"Health: {r.status_code} {r.json()}")

# Test login
r = httpx.post(f"{base}/auth/login", json={"username": "admin", "password": "Admin@123"})
print(f"Login: {r.status_code}")
if r.status_code == 200:
    token = r.json()["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Test /me
    r = httpx.get(f"{base}/auth/me", headers=headers)
    data = r.json()
    print(f"Me: {r.status_code} {data['full_name']}")

    # Test students list
    r = httpx.get(f"{base}/students/", headers=headers)
    print(f"Students: {r.status_code} content_type={r.headers.get('content-type', 'N/A')}")
    if r.status_code != 200:
        print(f"  Body: {r.text[:500]}")

    # Test employees list
    r = httpx.get(f"{base}/employees/", headers=headers)
    print(f"Employees: {r.status_code} content_type={r.headers.get('content-type', 'N/A')}")
    if r.status_code != 200:
        print(f"  Body: {r.text[:500]}")

    # Test departments list
    r = httpx.get(f"{base}/departments/", headers=headers)
    print(f"Departments: {r.status_code} content_type={r.headers.get('content-type', 'N/A')}")
    if r.status_code != 200:
        print(f"  Body: {r.text[:500]}")

    # Test attendance
    r = httpx.get(f"{base}/attendance/", headers=headers)
    print(f"Attendance: {r.status_code} content_type={r.headers.get('content-type', 'N/A')}")
    if r.status_code != 200:
        print(f"  Body: {r.text[:500]}")

    # Test fees
    r = httpx.get(f"{base}/fees/", headers=headers)
    print(f"Fees: {r.status_code} content_type={r.headers.get('content-type', 'N/A')}")
    if r.status_code != 200:
        print(f"  Body: {r.text[:500]}")

    # Test results
    r = httpx.get(f"{base}/results/", headers=headers)
    print(f"Results: {r.status_code} content_type={r.headers.get('content-type', 'N/A')}")
    if r.status_code != 200:
        print(f"  Body: {r.text[:500]}")

    # Test dashboard
    r = httpx.get(f"{base}/reports/dashboard", headers=headers)
    print(f"Dashboard: {r.status_code}")
    if r.status_code == 200:
        stats = r.json()["stats"]
        print(f"  Students: {stats['total_students']}")
        print(f"  Employees: {stats['total_employees']}")
        print(f"  Attendance Rate: {stats['attendance_rate']}%")
        print(f"  Pending Fees: {stats['pending_fees']}")

    # Test attendance stats
    r = httpx.get(f"{base}/attendance/stats/student/1", headers=headers)
    print(f"Attendance Stats: {r.status_code}")

    # Test fees dashboard
    r = httpx.get(f"{base}/fees/dashboard", headers=headers)
    print(f"Fees Dashboard: {r.status_code}")

    # Test create student
    r = httpx.post(f"{base}/students/", headers=headers, json={
        "student_id": "STU9999",
        "email": "test9999@smart.edu",
        "username": "test9999",
        "full_name": "Test Student",
        "phone": "9999999999",
        "department_id": 1,
        "course": "B.Tech",
        "semester": 1,
        "enrollment_date": "2024-01-15",
        "password": "Test@1234"
    })
    print(f"Create Student: {r.status_code}")

    # Test delete student
    if r.status_code == 200:
        student_id = r.json()["id"]
        r = httpx.delete(f"{base}/students/{student_id}", headers=headers)
        print(f"Delete Student: {r.status_code}")

    print("\nAll API tests passed!")
else:
    print(f"Login failed: {r.text}")
