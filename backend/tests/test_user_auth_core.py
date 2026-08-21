from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from app.modules.usuarios.constants import RolUsuario
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.passwords import (
    hashear_contrasena,
    verificar_contrasena,
)
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.usuarios.schemas import UsuarioCrear, UsuarioRespuesta
from app.modules.usuarios.service import UsuarioService


def datos_usuario(**cambios: object) -> UsuarioCrear:
    datos: dict[str, object] = {
        "email": "ADMIN@TopHouse.com",
        "nombre": "Administrador",
        "contrasena": "una-contrasena-segura",
    }
    datos.update(cambios)
    return UsuarioCrear.model_validate(datos)


def usuario_existente(**cambios: object) -> Usuario:
    ahora = datetime.now(UTC)
    datos: dict[str, object] = {
        "id": 1,
        "email": "admin@tophouse.com",
        "nombre": "Administrador",
        "password_hash": hashear_contrasena("una-contrasena-segura"),
        "rol": "administrador",
        "activo": True,
        "creado_en": ahora,
        "actualizado_en": ahora,
        "ultimo_acceso_en": None,
    }
    datos.update(cambios)
    return Usuario(**datos)


def test_argon2_hash_y_verificacion() -> None:
    contrasena = "una-contrasena-segura"

    resultado = hashear_contrasena(contrasena)

    assert resultado.startswith("$argon2")
    assert resultado != contrasena
    assert verificar_contrasena(contrasena, resultado) is True
    assert verificar_contrasena("incorrecta", resultado) is False


@pytest.mark.parametrize(
    "cambios",
    [
        {"email": "no-es-email"},
        {"nombre": ""},
        {"contrasena": "muy-corta"},
        {"rol": "superusuario"},
        {"activo": True},
    ],
)
def test_usuario_crear_rechaza_datos_invalidos(
    cambios: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        datos_usuario(**cambios)


def test_usuario_respuesta_no_expone_hash() -> None:
    respuesta = UsuarioRespuesta.model_validate(usuario_existente())

    assert respuesta.rol is RolUsuario.ADMINISTRADOR
    assert "password_hash" not in respuesta.model_dump()


def test_service_crea_hash_sin_guardar_contrasena_plana() -> None:
    repository = MagicMock(spec=UsuarioRepository)
    repository.crear.return_value = usuario_existente()
    service = UsuarioService(repository)
    datos = datos_usuario()

    service.crear(datos)

    password_hash = repository.crear.call_args.kwargs["password_hash"]
    assert datos.contrasena not in password_hash
    assert verificar_contrasena(datos.contrasena, password_hash)


def test_service_autentica_y_registra_acceso() -> None:
    repository = MagicMock(spec=UsuarioRepository)
    usuario = usuario_existente()
    repository.obtener_por_email.return_value = usuario
    repository.registrar_ultimo_acceso.return_value = usuario
    service = UsuarioService(repository)

    resultado = service.autenticar(
        " ADMIN@TOPHOUSE.COM ",
        "una-contrasena-segura",
    )

    assert resultado is usuario
    repository.obtener_por_email.assert_called_once_with("admin@tophouse.com")
    repository.registrar_ultimo_acceso.assert_called_once_with(usuario)


@pytest.mark.parametrize(
    "usuario",
    [
        None,
        usuario_existente(activo=False),
        usuario_existente(password_hash=hashear_contrasena("otra-contrasena")),
    ],
)
def test_service_rechaza_credenciales_o_usuario_inactivo(
    usuario: Usuario | None,
) -> None:
    repository = MagicMock(spec=UsuarioRepository)
    repository.obtener_por_email.return_value = usuario
    service = UsuarioService(repository)

    resultado = service.autenticar(
        "admin@tophouse.com",
        "una-contrasena-segura",
    )

    assert resultado is None
    repository.registrar_ultimo_acceso.assert_not_called()
