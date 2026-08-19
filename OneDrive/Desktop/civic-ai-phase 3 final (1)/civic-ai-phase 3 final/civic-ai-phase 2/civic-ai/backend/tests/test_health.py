from fastapi.testclient import TestClient

def test_health_endpoint_works(client: TestClient):
    """TEST 1: Health endpoint works."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "civic-ai-backend"
