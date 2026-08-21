from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.main import app
from app.modules.propiedades.models import Propiedad
from app.modules.usuarios.models import RegistroAuditoria, SesionUsuario, Usuario
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.usuarios.schemas import UsuarioCrear
from app.modules.usuarios.service import UsuarioService

client = TestClient(app, base_url="https://testserver")
CONTRASENA = "contrasena-segura-pruebas"


@pytest.fixture
def operador() -> Iterator[Usuario]:
    identificador = uuid4().hex[:10]
    with SessionLocal() as session:
        usuario = UsuarioService(UsuarioRepository(session)).crear(
            UsuarioCrear(
                email=f"test-rbac-{identificador}@example.com",
                nombre="Operador RBAC",
                contrasena=CONTRASENA,
            )
        )
        usuario_id = usuario.id

    yield usuario

    client.cookies.clear()
    with SessionLocal() as session:
        session.execute(
            delete(RegistroAuditoria).where(RegistroAuditoria.usuario_id == usuario_id)
        )
        session.execute(
            delete(SesionUsuario).where(SesionUsuario.usuario_id == usuario_id)
        )
        session.execute(delete(Usuario).where(Usuario.id == usuario_id))
        session.commit()


def datos_propiedad() -> dict[str, object]:
    identificador = uuid4().hex[:10]
    return {
        "codigo": f"TEST-RBAC-{identificador}",
        "titulo": "Propiedad con permisos",
        "descripcion": "Prueba de autorización y auditoría",
        "tipo_operacion": "venta",
        "tipo_propiedad": "casa",
        "precio": "100000.00",
        "moneda": "USD",
        "localidad": "Asunción",
    }


def test_api_administrativa_requiere_autenticacion() -> None:
    client.cookies.clear()
    respuesta = client.get("/api/v1/propiedades")
    assert respuesta.status_code == 401


def test_operador_crea_con_auditoria_pero_no_ejecuta_accion_admin(
    operador: Usuario,
) -> None:
    login = client.post(
        "/api/v1/auth/login",
        json={"email": operador.email, "contrasena": CONTRASENA},
    )
    csrf = client.cookies.get("tophouse_csrf")
    assert login.status_code == 200
    assert csrf is not None
    headers = {"X-CSRF-Token": csrf}

    creada = client.post(
        "/api/v1/propiedades",
        json=datos_propiedad(),
        headers=headers,
    )
    propiedad_id = creada.json()["id"]
    restringida = client.patch(
        f"/api/v1/propiedades/{propiedad_id}/admin",
        json={"estado": "publicada"},
        headers=headers,
    )

    assert creada.status_code == 201
    assert restringida.status_code == 403
    assert restringida.json()["detail"] == "Se requiere rol de administrador"

    with SessionLocal() as session:
        registro = session.scalar(
            select(RegistroAuditoria).where(
                RegistroAuditoria.usuario_id == operador.id,
                RegistroAuditoria.recurso_id == str(propiedad_id),
            )
        )
        assert registro is not None
        assert registro.accion == "propiedad.creada"
        assert registro.usuario_email == operador.email
        session.execute(delete(Propiedad).where(Propiedad.id == propiedad_id))
        session.commit()
