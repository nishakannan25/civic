from fastapi.testclient import TestClient

def test_authenticated_users_me_works(client: TestClient):
    """TEST 5: Authenticated /users/me works."""
    # Register and get access token
    reg_payload = {
        "name": "Alice Citizen",
        "email": "alice@example.com",
        "password": "Password123!",
    }
    reg_res = client.post("/auth/register", json=reg_payload)
    token = reg_res.json()["access_token"]

    # Call /users/me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["name"] == "Alice Citizen"
    assert user_data["email"] == "alice@example.com"
    assert user_data["role"] == "citizen"
    assert "password_hash" not in user_data

def test_unauthenticated_protected_endpoint_rejected(client: TestClient):
    """TEST 6: Unauthenticated protected endpoint is rejected."""
    response = client.get("/users/me")
    assert response.status_code == 401
