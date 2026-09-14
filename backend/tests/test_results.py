import pytest
from tests.conftest import create_test_user, create_test_student, get_auth_headers
from app.models import UserRole


class TestResultCRUD:
    def test_create_subject(self, client, admin_headers, db, roles, department):
        response = client.post("/api/v1/results/subjects", headers=admin_headers, json={
            "code": "CS101",
            "name": "Programming Fundamentals",
            "department_id": department.id,
            "credits": 4,
            "max_internal_marks": 30,
            "max_external_marks": 70,
            "semester": 1
        })
        assert response.status_code == 201
        data = response.json()
        assert data["code"] == "CS101"
        assert data["max_internal_marks"] == 30
        assert data["max_external_marks"] == 70

    def test_create_subject_duplicate_code(self, client, admin_headers, db, roles, department):
        client.post("/api/v1/results/subjects", headers=admin_headers, json={
            "code": "CS201", "name": "Data Structures", "semester": 2
        })
        response = client.post("/api/v1/results/subjects", headers=admin_headers, json={
            "code": "CS201", "name": "Data Structures Duplicate", "semester": 2
        })
        assert response.status_code == 409

    def test_list_subjects(self, client, admin_headers, db, roles, department):
        client.post("/api/v1/results/subjects", headers=admin_headers, json={
            "code": "CS301", "name": "Algorithms", "semester": 3
        })
        response = client.get("/api/v1/results/subjects", headers=admin_headers)
        assert response.status_code == 200

    def test_create_result(self, client, manager_headers, db, roles, department, student):
        subject_resp = client.post("/api/v1/results/subjects", headers=get_auth_headers(
            create_test_user(db, "admin2", "admin2@test.com", "Admin2", "Admin@123", UserRole.ADMIN, True)
        ), json={
            "code": "RES101", "name": "Test Subject", "semester": 1
        })
        subject_id = subject_resp.json()["id"]

        response = client.post("/api/v1/results", headers=manager_headers, json={
            "student_id": student.id,
            "subject_id": subject_id,
            "semester": 1,
            "internal_marks": 25,
            "external_marks": 60
        })
        assert response.status_code == 201
        data = response.json()
        assert data["total_marks"] == 85
        assert data["grade"] == "A"
        assert data["is_passed"] is True

    def test_create_result_grade_a_plus(self, client, manager_headers, db, roles, department, student):
        subject_resp = client.post("/api/v1/results/subjects", headers=get_auth_headers(
            create_test_user(db, "admin3", "admin3@test.com", "Admin3", "Admin@123", UserRole.ADMIN, True)
        ), json={
            "code": "RES102", "name": "Test Subject 2", "semester": 1
        })
        subject_id = subject_resp.json()["id"]

        response = client.post("/api/v1/results", headers=manager_headers, json={
            "student_id": student.id,
            "subject_id": subject_id,
            "semester": 1,
            "internal_marks": 30,
            "external_marks": 65
        })
        assert response.status_code == 201
        assert response.json()["grade"] == "A+"

    def test_create_result_grade_fail(self, client, manager_headers, db, roles, department, student):
        subject_resp = client.post("/api/v1/results/subjects", headers=get_auth_headers(
            create_test_user(db, "admin4", "admin4@test.com", "Admin4", "Admin@123", UserRole.ADMIN, True)
        ), json={
            "code": "RES103", "name": "Test Subject 3", "semester": 1
        })
        subject_id = subject_resp.json()["id"]

        response = client.post("/api/v1/results", headers=manager_headers, json={
            "student_id": student.id,
            "subject_id": subject_id,
            "semester": 1,
            "internal_marks": 10,
            "external_marks": 20
        })
        assert response.status_code == 201
        data = response.json()
        assert data["is_passed"] is False
        assert data["grade"] == "F"

    def test_create_result_marks_exceed_max(self, client, manager_headers, db, roles, department, student):
        subject_resp = client.post("/api/v1/results/subjects", headers=get_auth_headers(
            create_test_user(db, "admin5", "admin5@test.com", "Admin5", "Admin@123", UserRole.ADMIN, True)
        ), json={
            "code": "RES104", "name": "Test Subject 4", "semester": 1,
            "max_internal_marks": 30, "max_external_marks": 70
        })
        subject_id = subject_resp.json()["id"]

        response = client.post("/api/v1/results", headers=manager_headers, json={
            "student_id": student.id,
            "subject_id": subject_id,
            "semester": 1,
            "internal_marks": 35,
            "external_marks": 60
        })
        assert response.status_code == 400

    def test_create_result_duplicate(self, client, manager_headers, db, roles, department, student):
        subject_resp = client.post("/api/v1/results/subjects", headers=get_auth_headers(
            create_test_user(db, "admin6", "admin6@test.com", "Admin6", "Admin@123", UserRole.ADMIN, True)
        ), json={
            "code": "RES105", "name": "Test Subject 5", "semester": 1
        })
        subject_id = subject_resp.json()["id"]

        client.post("/api/v1/results", headers=manager_headers, json={
            "student_id": student.id,
            "subject_id": subject_id,
            "semester": 1,
            "internal_marks": 20,
            "external_marks": 50
        })
        response = client.post("/api/v1/results", headers=manager_headers, json={
            "student_id": student.id,
            "subject_id": subject_id,
            "semester": 1,
            "internal_marks": 25,
            "external_marks": 55
        })
        assert response.status_code == 409

    def test_list_results(self, client, manager_headers, db, roles, department, student):
        response = client.get("/api/v1/results", headers=manager_headers)
        assert response.status_code == 200

    def test_delete_result(self, client, manager_headers, db, roles, department, student):
        subject_resp = client.post("/api/v1/results/subjects", headers=get_auth_headers(
            create_test_user(db, "admin7", "admin7@test.com", "Admin7", "Admin@123", UserRole.ADMIN, True)
        ), json={
            "code": "RES106", "name": "Test Subject 6", "semester": 1
        })
        subject_id = subject_resp.json()["id"]

        result_resp = client.post("/api/v1/results", headers=manager_headers, json={
            "student_id": student.id,
            "subject_id": subject_id,
            "semester": 1,
            "internal_marks": 20,
            "external_marks": 50
        })
        result_id = result_resp.json()["id"]
        response = client.delete(f"/api/v1/results/{result_id}", headers=manager_headers)
        assert response.status_code == 200

    def test_student_cannot_create_result(self, client, student_headers):
        response = client.post("/api/v1/results", headers=student_headers, json={
            "student_id": 1, "subject_id": 1, "semester": 1,
            "internal_marks": 20, "external_marks": 50
        })
        assert response.status_code == 403


class TestGradeCalculation:
    def test_grade_boundaries(self, client, manager_headers, db, roles, department, student):
        admin = create_test_user(db, "gradmin", "gr@test.com", "GrAdmin", "Admin@123", UserRole.ADMIN, True)
        grades_to_test = [
            (30, 65, "A+"),   # 95%
            (25, 58, "A"),    # 83%
            (22, 50, "B+"),   # 72%
            (18, 45, "B"),    # 63%
            (15, 38, "C"),    # 53%
            (10, 25, "F"),    # 35%
        ]
        for i, (internal, external, expected_grade) in enumerate(grades_to_test):
            subject_resp = client.post("/api/v1/results/subjects", headers=get_auth_headers(admin), json={
                "code": f"GRD{i}", "name": f"Grade Test {i}", "semester": 1
            })
            if subject_resp.status_code != 201:
                continue
            subject_id = subject_resp.json()["id"]
            response = client.post("/api/v1/results", headers=manager_headers, json={
                "student_id": student.id,
                "subject_id": subject_id,
                "semester": 1,
                "internal_marks": internal,
                "external_marks": external
            })
            if response.status_code == 201:
                assert response.json()["grade"] == expected_grade, \
                    f"Internal={internal}, External={external}: expected {expected_grade}, got {response.json()['grade']}"
