import pytest
from fastapi.testclient import TestClient
from app.core.security import create_access_token


class TestAuthentication:
    def test_valid_login(self, client, admin_user):
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "Admin@123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
        assert "access_token" in data["tokens"]
        assert "refresh_token" in data["tokens"]
        assert data["user"]["username"] == "admin"

    def test_login_invalid_password(self, client, admin_user):
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_invalid_username(self, client, admin_user):
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "Admin@123"
        })
        assert response.status_code == 401

    def test_login_empty_credentials(self, client):
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_login_missing_password(self, client):
        response = client.post("/api/v1/auth/login", json={"username": "admin"})
        assert response.status_code == 422

    def test_get_current_user(self, client, admin_user, admin_headers):
        response = client.get("/api/v1/auth/me", headers=admin_headers)
        assert response.status_code == 200
        assert response.json()["username"] == "admin"

    def test_unauthorized_access(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code in [401, 403]

    def test_invalid_token(self, client):
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer invalidtoken123"
        })
        assert response.status_code in [401, 403]

    def test_token_refresh(self, client, admin_user):
        login_response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "Admin@123"
        })
        refresh_token = login_response.json()["tokens"]["refresh_token"]
        response = client.post("/api/v1/auth/refresh", params={
            "refresh_token": refresh_token
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_invalid_refresh_token(self, client):
        response = client.post("/api/v1/auth/refresh", params={
            "refresh_token": "invalidrefreshToken"
        })
        assert response.status_code == 401

    def test_logout(self, client):
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 200

    def test_change_password(self, client, admin_user, admin_headers):
        response = client.post("/api/v1/auth/change-password", json={
            "current_password": "Admin@123",
            "new_password": "NewAdmin@123"
        }, headers=admin_headers)
        assert response.status_code == 200

    def test_change_password_wrong_current(self, client, admin_user, admin_headers):
        response = client.post("/api/v1/auth/change-password", json={
            "current_password": "wrongpassword",
            "new_password": "NewAdmin@123"
        }, headers=admin_headers)
        assert response.status_code == 400

    def test_all_roles_can_login(self, client, admin_user, manager_user, employee_user, student_user):
        for username, password in [
            ("admin", "Admin@123"),
            ("manager", "Manager@123"),
            ("employee", "Employee@123"),
            ("student", "Student@123"),
        ]:
            response = client.post("/api/v1/auth/login", json={
                "username": username,
                "password": password
            })
            assert response.status_code == 200, f"Failed login for {username}"

    def test_role_authorization_admin(self, client, admin_headers):
        response = client.get("/api/v1/auth/roles", headers=admin_headers)
        assert response.status_code == 200

    def test_role_authorization_non_admin(self, client, employee_headers):
        response = client.get("/api/v1/auth/roles", headers=employee_headers)
        assert response.status_code == 403


class TestPasswordValidation:
    def test_password_too_short(self, client, admin_user, admin_headers):
        response = client.post("/api/v1/auth/change-password", json={
            "current_password": "Admin@123",
            "new_password": "short"
        }, headers=admin_headers)
        assert response.status_code in [400, 422]

    def test_password_no_uppercase(self, client, admin_user, admin_headers):
        response = client.post("/api/v1/auth/change-password", json={
            "current_password": "Admin@123",
            "new_password": "nouppercase1!"
        }, headers=admin_headers)
        assert response.status_code in [400, 422]
