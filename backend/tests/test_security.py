import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings
from app.core.security import SecurityHeadersMiddleware
from app.main import app


def configuracion_base(**cambios: object) -> Settings:
    datos: dict[str, object] = {
        "postgres_db": "tophouse",
        "postgres_user": "tophouse",
        "postgres_password": "secret",
        "_env_file": None,
    }
    datos.update(cambios)
    return Settings(**datos)  # type: ignore[arg-type]


def test_api_agrega_cabeceras_defensivas() -> None:
    response = TestClient(app).get("/health")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    assert response.headers["permissions-policy"] == (
        "camera=(), geolocation=(), microphone=()"
    )
    assert "strict-transport-security" not in response.headers


def test_cabeceras_de_produccion_exigen_https_y_bloquean_contenido() -> None:
    production_app = FastAPI()
    production_app.add_middleware(SecurityHeadersMiddleware, production=True)

    @production_app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    response = TestClient(production_app).get("/health")

    assert response.headers["strict-transport-security"] == (
        "max-age=31536000; includeSubDomains"
    )
    assert response.headers["content-security-policy"] == (
        "default-src 'none'; frame-ancestors 'none'"
    )


@pytest.mark.parametrize(
    ("cambios", "mensaje"),
    [
        ({"debug": True}, "DEBUG"),
        ({"session_cookie_secure": False}, "SESSION_COOKIE_SECURE"),
        ({"cors_origins": "http://admin.example"}, "CORS_ORIGINS"),
        ({"allowed_hosts": "*"}, "ALLOWED_HOSTS"),
    ],
)
def test_produccion_rechaza_configuracion_insegura(
    cambios: dict[str, object],
    mensaje: str,
) -> None:
    configuracion: dict[str, object] = {
        "app_env": "production",
        "cors_origins": "https://admin.example",
        "allowed_hosts": "api.example",
    }
    configuracion.update(cambios)
    with pytest.raises(ValidationError, match=mensaje):
        configuracion_base(**configuracion)


def test_produccion_acepta_configuracion_segura() -> None:
    configuracion = configuracion_base(
        app_env="production",
        cors_origins="https://admin.example",
        allowed_hosts="api.example",
    )

    assert configuracion.is_production is True
    assert configuracion.trusted_hosts == ["api.example"]
