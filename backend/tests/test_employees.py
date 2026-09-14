import pytest
from decimal import Decimal
from tests.conftest import create_test_user, create_test_employee, get_auth_headers
from app.models import UserRole


class TestEmployeeCRUD:
    def test_create_employee(self, client, admin_headers, db, roles, department):
        response = client.post("/api/v1/employees", headers=admin_headers, json={
            "employee_id": "EMP100",
            "email": "new@employee.com",
            "username": "newemployee",
            "full_name": "New Employee",
            "department_id": department.id,
            "designation": "Professor",
            "joining_date": "2024-01-01",
            "salary": 80000,
            "password": "Employee@123"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["employee_id"] == "EMP100"
        assert data["designation"] == "Professor"

    def test_create_employee_duplicate_id(self, client, admin_headers, db, roles, department, employee):
        response = client.post("/api/v1/employees", headers=admin_headers, json={
            "employee_id": "EMP001",
            "email": "another@employee.com",
            "username": "anotheremp",
            "full_name": "Another",
            "department_id": department.id,
            "designation": "HOD",
            "joining_date": "2024-01-01",
            "salary": 90000,
            "password": "Employee@123"
        })
        assert response.status_code == 409

    def test_list_employees(self, client, admin_headers, db, roles, department, employee):
        response = client.get("/api/v1/employees", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_employee_by_id(self, client, admin_headers, db, roles, department, employee):
        response = client.get(f"/api/v1/employees/{employee.id}", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["employee_id"] == "EMP001"

    def test_get_employee_not_found(self, client, admin_headers):
        response = client.get("/api/v1/employees/9999", headers=admin_headers)
        assert response.status_code == 404

    def test_update_employee(self, client, admin_headers, db, roles, department, employee):
        response = client.put(f"/api/v1/employees/{employee.id}", headers=admin_headers, json={
            "designation": "Senior Professor"
        })
        assert response.status_code == 200
        assert response.json()["designation"] == "Senior Professor"

    def test_delete_employee(self, client, admin_headers, db, roles, department):
        user = create_test_user(db, "delemp", "del@emp.com", "Del Emp", "Emp@123", UserRole.EMPLOYEE)
        emp = create_test_employee(db, user, department.id, "EMPDEL")
        response = client.delete(f"/api/v1/employees/{emp.id}", headers=admin_headers)
        assert response.status_code == 200

    def test_search_employees(self, client, admin_headers, db, roles, department, employee):
        response = client.get("/api/v1/employees?search=Test", headers=admin_headers)
        assert response.status_code == 200

    def test_pagination_employees(self, client, admin_headers, db, roles, department, employee):
        response = client.get("/api/v1/employees?page=1&page_size=3", headers=admin_headers)
        assert response.status_code == 200
        assert len(response.json()["items"]) <= 3

    def test_employee_cannot_create_employee(self, client, employee_headers):
        response = client.post("/api/v1/employees", headers=employee_headers, json={
            "employee_id": "EMP_X", "email": "x@x.com", "username": "x",
            "full_name": "X", "designation": "X", "joining_date": "2024-01-01",
            "salary": 50000, "password": "Test@1234"
        })
        assert response.status_code == 403
