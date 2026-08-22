from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.config import settings
from app.core.database import SessionLocal
from app.main import app
from app.modules.usuarios.models import SesionUsuario, Usuario
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.usuarios.schemas import UsuarioCrear
from app.modules.usuarios.service import UsuarioService

client = TestClient(app, base_url="https://testserver")
CONTRASENA = "contrasena-segura-pruebas"


@pytest.fixture(autouse=True)
def cookies_seguras_en_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "session_cookie_secure", True)


@pytest.fixture
def usuario_auth() -> Iterator[Usuario]:
    identificador = uuid4().hex[:10]
    email = f"test-auth-api-{identificador}@example.com"
    with SessionLocal() as session:
        usuario = UsuarioService(UsuarioRepository(session)).crear(
            UsuarioCrear(
                email=email,
                nombre="Usuario API",
                contrasena=CONTRASENA,
            )
        )
        usuario_id = usuario.id

    yield usuario

    client.cookies.clear()
    with SessionLocal() as session:
        session.execute(
            delete(SesionUsuario).where(SesionUsuario.usuario_id == usuario_id)
        )
        session.execute(delete(Usuario).where(Usuario.id == usuario_id))
        session.commit()


def iniciar_sesion(usuario: Usuario) -> None:
    respuesta = client.post(
        "/api/v1/auth/login",
        json={"email": usuario.email, "contrasena": CONTRASENA},
    )
    assert respuesta.status_code == 200


def test_login_configura_cookies_y_me_devuelve_usuario(
    usuario_auth: Usuario,
) -> None:
    respuesta = client.post(
        "/api/v1/auth/login",
        json={"email": usuario_auth.email, "contrasena": CONTRASENA},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["email"] == usuario_auth.email
    cookies = respuesta.headers.get_list("set-cookie")
    cookie_sesion = next(c for c in cookies if c.startswith("tophouse_session="))
    cookie_csrf = next(c for c in cookies if c.startswith("tophouse_csrf="))
    assert "HttpOnly" in cookie_sesion
    assert "Secure" in cookie_sesion
    assert "SameSite=lax" in cookie_sesion
    assert "HttpOnly" not in cookie_csrf
    assert "Secure" in cookie_csrf

    respuesta_me = client.get("/api/v1/auth/me")
    assert respuesta_me.status_code == 200
    assert respuesta_me.json()["id"] == usuario_auth.id


def test_login_rechaza_credenciales_invalidas(usuario_auth: Usuario) -> None:
    respuesta = client.post(
        "/api/v1/auth/login",
        json={"email": usuario_auth.email, "contrasena": "incorrecta"},
    )

    assert respuesta.status_code == 401
    assert respuesta.json() == {"detail": "Credenciales inválidas"}
    assert "tophouse_session" not in respuesta.cookies


def test_login_rechaza_usuario_inactivo(usuario_auth: Usuario) -> None:
    with SessionLocal() as session:
        usuario = session.get(Usuario, usuario_auth.id)
        assert usuario is not None
        usuario.activo = False
        session.commit()

    respuesta = client.post(
        "/api/v1/auth/login",
        json={"email": usuario_auth.email, "contrasena": CONTRASENA},
    )

    assert respuesta.status_code == 401


def test_logout_exige_csrf_y_revoca_sesion(usuario_auth: Usuario) -> None:
    iniciar_sesion(usuario_auth)
    csrf_token = client.cookies.get("tophouse_csrf")
    assert csrf_token is not None

    sin_csrf = client.post("/api/v1/auth/logout")
    csrf_invalido = client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": "token-incorrecto"},
    )
    assert sin_csrf.status_code == 403
    assert csrf_invalido.status_code == 403

    respuesta = client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )
    assert respuesta.status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401

    with SessionLocal() as session:
        sesion = session.scalar(
            select(SesionUsuario).where(SesionUsuario.usuario_id == usuario_auth.id)
        )
        assert sesion is not None
        assert sesion.revocada_en is not None


def test_sesion_expirada_no_autentica(usuario_auth: Usuario) -> None:
    iniciar_sesion(usuario_auth)
    with SessionLocal() as session:
        sesion = session.scalar(
            select(SesionUsuario).where(SesionUsuario.usuario_id == usuario_auth.id)
        )
        assert sesion is not None
        sesion.expira_en = datetime.now(UTC) - timedelta(seconds=1)
        session.commit()

    assert client.get("/api/v1/auth/me").status_code == 401
