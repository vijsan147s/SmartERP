import pytest
from datetime import date, timedelta
from tests.conftest import create_test_user, create_test_student, get_auth_headers
from app.models import UserRole


class TestAttendanceCRUD:
    def test_mark_attendance(self, client, manager_headers, db, roles, department, student):
        response = client.post("/api/v1/attendance", headers=manager_headers, json={
            "student_id": student.id,
            "date": str(date.today()),
            "status": "PRESENT",
            "remarks": "On time"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "PRESENT"
        assert data["student_id"] == student.id

    def test_mark_attendance_absent(self, client, manager_headers, db, roles, department, student):
        response = client.post("/api/v1/attendance", headers=manager_headers, json={
            "student_id": student.id,
            "date": str(date.today() + timedelta(days=1)),
            "status": "ABSENT"
        })
        assert response.status_code == 201
        assert response.json()["status"] == "ABSENT"

    def test_mark_attendance_duplicate(self, client, manager_headers, db, roles, department, student):
        client.post("/api/v1/attendance", headers=manager_headers, json={
            "student_id": student.id,
            "date": str(date.today() + timedelta(days=2)),
            "status": "PRESENT"
        })
        response = client.post("/api/v1/attendance", headers=manager_headers, json={
            "student_id": student.id,
            "date": str(date.today() + timedelta(days=2)),
            "status": "ABSENT"
        })
        assert response.status_code == 409

    def test_mark_attendance_invalid_student(self, client, manager_headers, db, roles):
        response = client.post("/api/v1/attendance", headers=manager_headers, json={
            "student_id": 9999,
            "date": str(date.today()),
            "status": "PRESENT"
        })
        assert response.status_code == 404

    def test_list_attendance(self, client, manager_headers, db, roles, department, student):
        client.post("/api/v1/attendance", headers=manager_headers, json={
            "student_id": student.id,
            "date": str(date.today() + timedelta(days=3)),
            "status": "LATE"
        })
        response = client.get("/api/v1/attendance", headers=manager_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_update_attendance(self, client, manager_headers, db, roles, department, student):
        create_resp = client.post("/api/v1/attendance", headers=manager_headers, json={
            "student_id": student.id,
            "date": str(date.today() + timedelta(days=4)),
            "status": "PRESENT"
        })
        att_id = create_resp.json()["id"]
        response = client.put(f"/api/v1/attendance/{att_id}", headers=manager_headers, json={
            "status": "LATE"
        })
        assert response.status_code == 200
        assert response.json()["status"] == "LATE"

    def test_delete_attendance(self, client, manager_headers, db, roles, department, student):
        create_resp = client.post("/api/v1/attendance", headers=manager_headers, json={
            "student_id": student.id,
            "date": str(date.today() + timedelta(days=5)),
            "status": "EXCUSED"
        })
        att_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/attendance/{att_id}", headers=manager_headers)
        assert response.status_code == 200

    def test_student_attendance_stats(self, client, manager_headers, db, roles, department, student):
        response = client.get(f"/api/v1/attendance/stats/student/{student.id}", headers=manager_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_days" in data
        assert "attendance_percentage" in data
        assert "risk_level" in data
        assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]

    def test_attendance_stats_not_found(self, client, manager_headers):
        response = client.get("/api/v1/attendance/stats/student/9999", headers=manager_headers)
        assert response.status_code == 404

    def test_student_cannot_mark_attendance(self, client, student_headers):
        response = client.post("/api/v1/attendance", headers=student_headers, json={
            "student_id": 1, "date": str(date.today()), "status": "PRESENT"
        })
        assert response.status_code == 403
