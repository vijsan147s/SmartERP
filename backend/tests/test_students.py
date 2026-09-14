import pytest
from app.core.security import create_access_token
from tests.conftest import create_test_user, create_test_student, create_test_department, get_auth_headers
from app.models import UserRole


class TestStudentCRUD:
    def test_create_student(self, client, admin_headers, db, roles, department):
        response = client.post("/api/v1/students", headers=admin_headers, json={
            "student_id": "STU100",
            "email": "new@student.com",
            "username": "newstudent",
            "full_name": "New Student",
            "phone": "9876543210",
            "department_id": department.id,
            "course": "B.Tech",
            "semester": 1,
            "enrollment_date": "2024-08-15",
            "password": "Student@123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["student_id"] == "STU100"
        assert data["email"] == "new@student.com"
        assert data["full_name"] == "New Student"

    def test_create_student_duplicate_id(self, client, admin_headers, db, roles, department, student):
        response = client.post("/api/v1/students", headers=admin_headers, json={
            "student_id": "STU001",
            "email": "another@student.com",
            "username": "anotherstudent",
            "full_name": "Another Student",
            "course": "B.Tech",
            "semester": 1,
            "enrollment_date": "2024-08-15",
            "password": "Student@123"
        })
        assert response.status_code == 409

    def test_create_student_duplicate_email(self, client, admin_headers, db, roles, department, student):
        response = client.post("/api/v1/students", headers=admin_headers, json={
            "student_id": "STU999",
            "email": "test@student.com",
            "username": "uniqueusername",
            "full_name": "Another Student",
            "course": "B.Tech",
            "semester": 1,
            "enrollment_date": "2024-08-15",
            "password": "Student@123"
        })
        assert response.status_code == 409

    def test_list_students(self, client, admin_headers, db, roles, department, student):
        response = client.get("/api/v1/students", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    def test_get_student_by_id(self, client, admin_headers, db, roles, department, student):
        response = client.get(f"/api/v1/students/{student.id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["student_id"] == "STU001"

    def test_get_student_not_found(self, client, admin_headers):
        response = client.get("/api/v1/students/9999", headers=admin_headers)
        assert response.status_code == 404

    def test_update_student(self, client, admin_headers, db, roles, department, student):
        response = client.put(f"/api/v1/students/{student.id}", headers=admin_headers, json={
            "full_name": "Updated Student Name"
        })
        assert response.status_code == 200
        assert response.json()["full_name"] == "Updated Student Name"

    def test_delete_student(self, client, admin_headers, db, roles, department):
        user = create_test_user(db, "deletable", "delete@student.com", "Delete Me", "Student@123", UserRole.STUDENT)
        stu = create_test_student(db, user, department.id, "STUDEL")
        response = client.delete(f"/api/v1/students/{stu.id}", headers=admin_headers)
        assert response.status_code == 200

    def test_delete_student_not_found(self, client, admin_headers):
        response = client.delete("/api/v1/students/9999", headers=admin_headers)
        assert response.status_code == 404

    def test_search_students(self, client, admin_headers, db, roles, department, student):
        response = client.get("/api/v1/students?search=Test", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_filter_students_by_semester(self, client, admin_headers, db, roles, department, student):
        response = client.get("/api/v1/students?semester=1", headers=admin_headers)
        assert response.status_code == 200

    def test_pagination_students(self, client, admin_headers, db, roles, department, student):
        response = client.get("/api/v1/students?page=1&page_size=5", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()["items"]) <= 5

    def test_student_cannot_list_students(self, client, student_headers):
        response = client.get("/api/v1/students", headers=student_headers)
        assert response.status_code == 403

    def test_student_cannot_create_student(self, client, student_headers):
        response = client.post("/api/v1/students", headers=student_headers, json={
            "student_id": "STU_X", "email": "x@x.com", "username": "x",
            "full_name": "X", "course": "X", "semester": 1,
            "enrollment_date": "2024-01-01", "password": "Test@1234"
        })
        assert response.status_code == 403

    def test_manager_can_create_student(self, client, manager_headers, db, roles, department):
        response = client.post("/api/v1/students", headers=manager_headers, json={
            "student_id": "STU200",
            "email": "mgr@student.com",
            "username": "mgrstudent",
            "full_name": "Mgr Student",
            "course": "B.Tech",
            "semester": 1,
            "enrollment_date": "2024-08-15",
            "password": "Student@123"
        })
        assert response.status_code == 201
