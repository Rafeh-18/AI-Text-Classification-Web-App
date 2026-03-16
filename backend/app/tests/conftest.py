import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import app
from backend.app.database.database import Base, get_db

# Use a separate in-memory SQLite DB for tests — never touches app.db
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the DB dependency so tests use the test DB
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def reset_db():
    """Drop and recreate all tables before each test for a clean slate."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """Register a user and return their credentials."""
    payload = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "Password123",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    return payload


@pytest.fixture
def auth_headers(client, registered_user):
    """Log in and return Authorization headers."""
    response = client.post("/api/v1/auth/login", json={
        "email": registered_user["email"],
        "password": registered_user["password"],
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}