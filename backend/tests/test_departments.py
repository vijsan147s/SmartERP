import pytest
from tests.conftest import create_test_department, get_auth_headers
from app.models import UserRole


class TestDepartmentCRUD:
    def test_create_department(self, client, admin_headers, db, roles):
        response = client.post("/api/v1/departments", headers=admin_headers, json={
            "name": "Mathematics",
            "code": "MATH",
            "description": "Mathematics Department"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Mathematics"
        assert data["code"] == "MATH"

    def test_create_department_duplicate_name(self, client, admin_headers, db, roles, department):
        response = client.post("/api/v1/departments", headers=admin_headers, json={
            "name": "Computer Science",
            "code": "NEW",
            "description": "Duplicate"
        })
        assert response.status_code == 409

    def test_create_department_duplicate_code(self, client, admin_headers, db, roles, department):
        response = client.post("/api/v1/departments", headers=admin_headers, json={
            "name": "New Department",
            "code": "CS",
            "description": "Duplicate code"
        })
        assert response.status_code == 409

    def test_list_departments(self, client, admin_headers, db, roles, department):
        response = client.get("/api/v1/departments", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_department_by_id(self, client, admin_headers, db, roles, department):
        response = client.get(f"/api/v1/departments/{department.id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["name"] == "Computer Science"

    def test_get_department_not_found(self, client, admin_headers):
        response = client.get("/api/v1/departments/9999", headers=admin_headers)
        assert response.status_code == 404

    def test_update_department(self, client, admin_headers, db, roles, department):
        response = client.put(f"/api/v1/departments/{department.id}", headers=admin_headers, json={
            "description": "Updated description"
        })
        assert response.status_code == 200
        assert response.json()["description"] == "Updated description"

    def test_delete_department(self, client, admin_headers, db, roles):
        dept = create_test_department(db, "Temp Dept", "TMP")
        response = client.delete(f"/api/v1/departments/{dept.id}", headers=admin_headers)
        assert response.status_code == 200

    def test_manager_can_list_departments(self, client, manager_headers, db, roles, department):
        response = client.get("/api/v1/departments", headers=manager_headers)
        assert response.status_code == 200

    def test_employee_cannot_create_department(self, client, employee_headers):
        response = client.post("/api/v1/departments", headers=employee_headers, json={
            "name": "Test", "code": "TST"
        })
        assert response.status_code == 403

    def test_manager_cannot_create_department(self, client, manager_headers):
        response = client.post("/api/v1/departments", headers=manager_headers, json={
            "name": "Physics", "code": "PHY"
        })
        assert response.status_code == 403
