from fastapi.testclient import TestClient

from flowlens.main import app


client = TestClient(app)


def test_health_check_returns_service_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "name": "FlowLens API",
        "status": "healthy",
        "version": "0.1.0",
    }