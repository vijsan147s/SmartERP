import pytest
from decimal import Decimal
from tests.conftest import create_test_user, create_test_student, get_auth_headers
from app.models import UserRole


class TestFeeCRUD:
    def test_create_fee(self, client, manager_headers, db, roles, department, student):
        response = client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": student.id,
            "academic_year": "2024-25",
            "semester": 1,
            "total_amount": 50000,
            "due_date": "2024-12-31"
        })
        assert response.status_code == 201
        data = response.json()
        assert Decimal(str(data["total_amount"])) == Decimal("50000")
        assert Decimal(str(data["pending_amount"])) == Decimal("50000")
        assert data["status"] == "PENDING"

    def test_create_fee_duplicate(self, client, manager_headers, db, roles, department, student):
        client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": student.id,
            "academic_year": "2024-25",
            "semester": 2,
            "total_amount": 45000
        })
        response = client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": student.id,
            "academic_year": "2024-25",
            "semester": 2,
            "total_amount": 45000
        })
        assert response.status_code == 409

    def test_create_fee_invalid_student(self, client, manager_headers, db, roles):
        response = client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": 9999,
            "academic_year": "2024-25",
            "semester": 1,
            "total_amount": 50000
        })
        assert response.status_code == 404

    def test_list_fees(self, client, manager_headers, db, roles, department, student):
        client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": student.id,
            "academic_year": "2025-26",
            "semester": 1,
            "total_amount": 60000
        })
        response = client.get("/api/v1/fees", headers=manager_headers)
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    def test_get_fee_by_id(self, client, manager_headers, db, roles, department, student):
        create_resp = client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": student.id,
            "academic_year": "2026-27",
            "semester": 1,
            "total_amount": 55000
        })
        fee_id = create_resp.json()["id"]
        response = client.get(f"/api/v1/fees/{fee_id}", headers=manager_headers)
        assert response.status_code == 200

    def test_update_fee(self, client, manager_headers, db, roles, department, student):
        create_resp = client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": student.id,
            "academic_year": "2027-28",
            "semester": 1,
            "total_amount": 50000
        })
        fee_id = create_resp.json()["id"]
        response = client.put(f"/api/v1/fees/{fee_id}", headers=manager_headers, json={
            "total_amount": 55000
        })
        assert response.status_code == 200
        assert Decimal(response.json()["pending_amount"]) == Decimal("55000")

    def test_make_payment(self, client, manager_headers, db, roles, department, student):
        create_resp = client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": student.id,
            "academic_year": "2028-29",
            "semester": 1,
            "total_amount": 50000
        })
        fee_id = create_resp.json()["id"]
        response = client.post(f"/api/v1/fees/{fee_id}/payments", headers=manager_headers, json={
            "fee_id": fee_id,
            "amount": 20000,
            "payment_date": "2024-11-15",
            "payment_method": "UPI",
            "receipt_number": "RCP001"
        })
        assert response.status_code == 201

    def test_payment_exceeds_pending(self, client, manager_headers, db, roles, department, student):
        create_resp = client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": student.id,
            "academic_year": "2029-30",
            "semester": 1,
            "total_amount": 10000
        })
        fee_id = create_resp.json()["id"]
        response = client.post(f"/api/v1/fees/{fee_id}/payments", headers=manager_headers, json={
            "fee_id": fee_id,
            "amount": 20000,
            "payment_date": "2024-11-15",
            "payment_method": "CASH",
            "receipt_number": "RCP002"
        })
        assert response.status_code == 400

    def test_fee_dashboard(self, client, manager_headers, db, roles, department, student):
        response = client.get("/api/v1/fees/dashboard", headers=manager_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_fees" in data
        assert "total_collected" in data
        assert "collection_rate" in data

    def test_delete_fee(self, client, manager_headers, db, roles, department, student):
        create_resp = client.post("/api/v1/fees", headers=manager_headers, json={
            "student_id": student.id,
            "academic_year": "2030-31",
            "semester": 1,
            "total_amount": 50000
        })
        fee_id = create_resp.json()["id"]
        response = client.delete(f"/api/v1/fees/{fee_id}", headers=manager_headers)
        assert response.status_code == 200

    def test_employee_cannot_create_fee(self, client, employee_headers):
        response = client.post("/api/v1/fees", headers=employee_headers, json={
            "student_id": 1, "academic_year": "2024-25", "semester": 1, "total_amount": 50000
        })
        assert response.status_code == 403
