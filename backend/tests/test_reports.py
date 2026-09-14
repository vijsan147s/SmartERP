import pytest


class TestReports:
    def test_dashboard_report(self, client, admin_headers):
        response = client.get("/api/v1/reports/dashboard", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "employee_student_distribution" in data
        assert "attendance_trend" in data

    def test_students_report(self, client, admin_headers):
        response = client.get("/api/v1/reports/students", headers=admin_headers)
        assert response.status_code == 200

    def test_employees_report(self, client, admin_headers):
        response = client.get("/api/v1/reports/employees", headers=admin_headers)
        assert response.status_code == 200

    def test_attendance_report(self, client, admin_headers):
        response = client.get("/api/v1/reports/attendance", headers=admin_headers)
        assert response.status_code == 200

    def test_fees_report(self, client, admin_headers):
        response = client.get("/api/v1/reports/fees", headers=admin_headers)
        assert response.status_code == 200

    def test_departments_report(self, client, admin_headers):
        response = client.get("/api/v1/reports/departments", headers=admin_headers)
        assert response.status_code == 200

    def test_academic_performance_report(self, client, admin_headers):
        response = client.get("/api/v1/reports/academic-performance", headers=admin_headers)
        assert response.status_code == 200

    def test_csv_export_students(self, client, admin_headers):
        response = client.get("/api/v1/reports/students?format=csv", headers=admin_headers)
        assert response.status_code == 200

    def test_csv_export_employees(self, client, admin_headers):
        response = client.get("/api/v1/reports/employees?format=csv", headers=admin_headers)
        assert response.status_code == 200

    def test_csv_export_attendance(self, client, admin_headers):
        response = client.get("/api/v1/reports/attendance?format=csv", headers=admin_headers)
        assert response.status_code == 200

    def test_csv_export_fees(self, client, admin_headers):
        response = client.get("/api/v1/reports/fees?format=csv", headers=admin_headers)
        assert response.status_code == 200

    def test_csv_export_departments(self, client, admin_headers):
        response = client.get("/api/v1/reports/departments?format=csv", headers=admin_headers)
        assert response.status_code == 200

    def test_csv_export_academic(self, client, admin_headers):
        response = client.get("/api/v1/reports/academic-performance?format=csv", headers=admin_headers)
        assert response.status_code == 200

    def test_reports_require_auth(self, client):
        for endpoint in [
            "/api/v1/reports/dashboard",
            "/api/v1/reports/students",
            "/api/v1/reports/employees",
        ]:
            response = client.get(endpoint)
            assert response.status_code in [401, 403]

    def test_student_cannot_access_reports(self, client, student_headers):
        response = client.get("/api/v1/reports/dashboard", headers=student_headers)
        assert response.status_code == 403

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SmartERP"

    def test_openapi_json(self, client):
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        assert "paths" in response.json()
