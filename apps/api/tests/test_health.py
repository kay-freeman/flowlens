from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

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


def test_readiness_check_returns_database_status(monkeypatch) -> None:
    monkeypatch.setattr(
        "flowlens.main.check_database_connection",
        lambda: True,
    )

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "name": "FlowLens API",
        "status": "ready",
        "database": "connected",
    }


def test_readiness_check_returns_503_when_database_is_unavailable(
    monkeypatch,
) -> None:
    def unavailable_database() -> bool:
        raise SQLAlchemyError("Database unavailable")

    monkeypatch.setattr(
        "flowlens.main.check_database_connection",
        unavailable_database,
    )

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Database connection unavailable.",
    }