from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.user import User

def test_database_connection_works(db_session: Session):
    """TEST 2: Database connection works."""
    result = db_session.execute(text("SELECT 1")).scalar()
    assert result == 1

def test_user_registration_works(client: TestClient, db_session: Session):
    """TEST 3: User registration works."""
    payload = {
        "name": "Jane Citizen",
        "email": "jane@example.com",
        "password": "SecurePassword123",
        "phone": "+919876543210",
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "jane@example.com"
    assert data["user"]["name"] == "Jane Citizen"
    assert "password_hash" not in data["user"]
    assert "password" not in data["user"]

    # Verify user exists in database with hashed password
    db_user = db_session.query(User).filter(User.email == "jane@example.com").first()
    assert db_user is not None
    assert db_user.password_hash != "SecurePassword123"

def test_user_login_works(client: TestClient):
    """TEST 4: User login works."""
    # Register user first
    reg_payload = {
        "name": "John Doe",
        "email": "john@example.com",
        "password": "MySecretPassword",
    }
    client.post("/auth/register", json=reg_payload)

    # Attempt login
    login_payload = {
        "email": "john@example.com",
        "password": "MySecretPassword",
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "john@example.com"
