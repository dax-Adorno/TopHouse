from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "TopHouse API",
    }


@patch("app.main.comprobar_dependencias")
def test_readiness_returns_ok_when_dependencies_are_available(
    comprobar_dependencias_mock: Mock,
) -> None:
    comprobar_dependencias_mock.return_value = {
        "database": "ok",
        "storage": "ok",
    }

    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "checks": {"database": "ok", "storage": "ok"},
    }


@patch("app.main.comprobar_dependencias")
def test_readiness_returns_503_when_a_dependency_is_unavailable(
    comprobar_dependencias_mock: Mock,
) -> None:
    comprobar_dependencias_mock.return_value = {
        "database": "ok",
        "storage": "unavailable",
    }

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "checks": {"database": "ok", "storage": "unavailable"},
    }
