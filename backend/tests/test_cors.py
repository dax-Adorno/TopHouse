from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_cors_permite_frontend_local_con_credenciales() -> None:
    response = client.options(
        "/api/v1/auth/me",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert response.headers["access-control-allow-credentials"] == "true"
