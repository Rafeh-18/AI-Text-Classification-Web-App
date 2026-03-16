"""
Tests for /api/v1/auth endpoints:
  POST /register
  POST /login
  GET  /me
"""


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

class TestRegister:

    def test_register_success(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "username": "newuser",
            "password": "Password123",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        # password must never be returned
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client, registered_user):
        response = client.post("/api/v1/auth/register", json={
            "email": registered_user["email"],   # same email
            "username": "differentuser",
            "password": "Password123",
        })
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()

    def test_register_duplicate_username(self, client, registered_user):
        response = client.post("/api/v1/auth/register", json={
            "email": "different@example.com",
            "username": registered_user["username"],   # same username
            "password": "Password123",
        })
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()

    def test_register_invalid_email(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "not-an-email",
            "username": "someuser",
            "password": "Password123",
        })
        assert response.status_code == 422

    def test_register_password_too_short(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "username": "someuser",
            "password": "123",   # min is 6
        })
        assert response.status_code == 422

    def test_register_username_too_short(self, client):
        response = client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "username": "ab",   # min is 3
            "password": "Password123",
        })
        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:

    def test_login_success(self, client, registered_user):
        response = client.post("/api/v1/auth/login", json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, client, registered_user):
        response = client.post("/api/v1/auth/login", json={
            "email": registered_user["email"],
            "password": "WrongPassword!",
        })
        assert response.status_code == 401

    def test_login_wrong_email(self, client):
        response = client.post("/api/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "Password123",
        })
        assert response.status_code == 401

    def test_login_missing_password(self, client, registered_user):
        response = client.post("/api/v1/auth/login", json={
            "email": registered_user["email"],
        })
        assert response.status_code == 422


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------

class TestGetMe:

    def test_get_me_success(self, client, registered_user, auth_headers):
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == registered_user["email"]
        assert data["username"] == registered_user["username"]

    def test_get_me_no_token(self, client):
        response = client.get("/api/v1/auth/me")
        # FastAPI's HTTPBearer returns 403 or 401 depending on version
        assert response.status_code in (401, 403)

    def test_get_me_invalid_token(self, client):
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "Bearer this.is.not.valid"
        })
        assert response.status_code == 401

    def test_get_me_malformed_header(self, client):
        response = client.get("/api/v1/auth/me", headers={
            "Authorization": "NotBearer sometoken"
        })
        # FastAPI's HTTPBearer returns 403 or 401 depending on version
        assert response.status_code in (401, 403)