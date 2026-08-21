from collections.abc import Iterator
from uuid import uuid4

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.usuarios.exceptions import UsuarioDuplicadoError
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.passwords import hashear_contrasena
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.usuarios.schemas import UsuarioCrear


@pytest.fixture
def session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.execute(delete(Usuario).where(Usuario.email.like("test-auth-%")))
        session.commit()
        session.close()


@pytest.fixture
def repository(session: Session) -> UsuarioRepository:
    return UsuarioRepository(session)


def datos_usuario(*, email: str | None = None) -> UsuarioCrear:
    identificador = uuid4().hex[:10]
    return UsuarioCrear.model_validate(
        {
            "email": email or f"test-auth-{identificador}@example.com",
            "nombre": "Usuario de integración",
            "contrasena": "una-contrasena-de-prueba",
        }
    )


def test_repository_crea_normaliza_y_recupera_usuario(
    repository: UsuarioRepository,
) -> None:
    datos = datos_usuario(email="TEST-AUTH-UPPER@EXAMPLE.COM")

    usuario = repository.crear(
        datos,
        password_hash=hashear_contrasena(datos.contrasena),
    )
    recuperado = repository.obtener_por_email("TEST-AUTH-UPPER@EXAMPLE.COM")

    assert usuario.email == "test-auth-upper@example.com"
    assert usuario.rol == "operador"
    assert usuario.activo is True
    assert recuperado is not None
    assert recuperado.id == usuario.id


def test_repository_rechaza_email_duplicado(
    repository: UsuarioRepository,
) -> None:
    datos = datos_usuario()
    password_hash = hashear_contrasena(datos.contrasena)
    repository.crear(datos, password_hash=password_hash)

    with pytest.raises(UsuarioDuplicadoError):
        repository.crear(datos, password_hash=password_hash)


def test_repository_registra_ultimo_acceso(
    repository: UsuarioRepository,
) -> None:
    datos = datos_usuario()
    usuario = repository.crear(
        datos,
        password_hash=hashear_contrasena(datos.contrasena),
    )

    actualizado = repository.registrar_ultimo_acceso(usuario)

    assert actualizado.ultimo_acceso_en is not None
