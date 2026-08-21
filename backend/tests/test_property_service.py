from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from app.modules.propiedades.exceptions import (
    PropiedadNoEncontradaError,
    TransicionEstadoInvalidaError,
)
from app.modules.propiedades.models import Propiedad
from app.modules.propiedades.repository import PropiedadRepository
from app.modules.propiedades.schemas import (
    PropiedadActualizar,
    PropiedadAdminActualizar,
    PropiedadCrear,
)
from app.modules.propiedades.service import PropiedadService
from app.modules.propiedades.slug import normalizar_slug, slug_con_sufijo


def datos_creacion(**cambios: object) -> PropiedadCrear:
    datos: dict[str, object] = {
        "codigo": "TH-001",
        "titulo": "Casa Ñandutí en Asunción",
        "descripcion": "Casa de prueba",
        "tipo_operacion": "venta",
        "tipo_propiedad": "casa",
        "localidad": "Asunción",
    }
    datos.update(cambios)
    return PropiedadCrear.model_validate(datos)


def propiedad_existente(**cambios: object) -> Propiedad:
    ahora = datetime.now(UTC)
    datos: dict[str, object] = {
        "id": 1,
        "codigo": "TH-001",
        "slug": "casa-nanduti-en-asuncion",
        "titulo": "Casa Ñandutí en Asunción",
        "descripcion": "Casa de prueba",
        "tipo_operacion": "venta",
        "tipo_propiedad": "casa",
        "localidad": "Asunción",
        "estado": "borrador",
        "destacada": False,
        "creado_en": ahora,
        "actualizado_en": ahora,
    }
    datos.update(cambios)
    return Propiedad(**datos)


@pytest.fixture
def repository() -> MagicMock:
    return MagicMock(spec=PropiedadRepository)


@pytest.fixture
def service(repository: MagicMock) -> PropiedadService:
    return PropiedadService(repository)


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Casa Ñandutí en Asunción", "casa-nanduti-en-asuncion"),
        ("  Departamento / Centro  ", "departamento-centro"),
        ("***", "propiedad"),
    ],
)
def test_normalizar_slug(texto: str, esperado: str) -> None:
    assert normalizar_slug(texto) == esperado


def test_slug_con_sufijo_respeta_longitud_maxima() -> None:
    slug = slug_con_sufijo("a" * 180, 25)

    assert len(slug) == 180
    assert slug.endswith("-25")


def test_service_crea_con_slug_normalizado(
    service: PropiedadService,
    repository: MagicMock,
) -> None:
    datos = datos_creacion()
    creada = propiedad_existente()
    repository.existe_slug.return_value = False
    repository.crear.return_value = creada

    resultado = service.crear(datos)

    assert resultado is creada
    repository.crear.assert_called_once_with(
        datos,
        slug="casa-nanduti-en-asuncion",
    )


def test_service_agrega_sufijo_si_slug_existe(
    service: PropiedadService,
    repository: MagicMock,
) -> None:
    repository.existe_slug.side_effect = [True, True, False]
    repository.crear.return_value = propiedad_existente(
        slug="casa-nanduti-en-asuncion-3"
    )

    service.crear(datos_creacion())

    assert repository.crear.call_args.kwargs["slug"] == ("casa-nanduti-en-asuncion-3")


def test_service_obtener_inexistente_lanza_error(
    service: PropiedadService,
    repository: MagicMock,
) -> None:
    repository.obtener_por_id.return_value = None

    with pytest.raises(PropiedadNoEncontradaError):
        service.obtener_por_id(999)


def test_service_actualiza_patch_comun(
    service: PropiedadService,
    repository: MagicMock,
) -> None:
    propiedad = propiedad_existente()
    cambios = PropiedadActualizar.model_validate({"titulo": "Nuevo título"})
    repository.obtener_por_id.return_value = propiedad
    repository.actualizar.return_value = propiedad

    resultado = service.actualizar(propiedad.id, cambios)

    assert resultado is propiedad
    repository.actualizar.assert_called_once_with(propiedad, cambios)


@pytest.mark.parametrize(
    ("actual", "nuevo"),
    [
        ("borrador", "publicada"),
        ("publicada", "reservada"),
        ("reservada", "vendida"),
        ("alquilada", "publicada"),
        ("no_disponible", "borrador"),
    ],
)
def test_service_permite_transiciones_validas(
    service: PropiedadService,
    repository: MagicMock,
    actual: str,
    nuevo: str,
) -> None:
    propiedad = propiedad_existente(estado=actual)
    cambios = PropiedadAdminActualizar.model_validate({"estado": nuevo})
    repository.obtener_por_id.return_value = propiedad
    repository.actualizar.return_value = propiedad

    service.actualizar_admin(propiedad.id, cambios)

    repository.actualizar.assert_called_once_with(propiedad, cambios)


@pytest.mark.parametrize(
    ("actual", "nuevo"),
    [
        ("borrador", "vendida"),
        ("pausada", "alquilada"),
        ("vendida", "publicada"),
    ],
)
def test_service_rechaza_transiciones_invalidas(
    service: PropiedadService,
    repository: MagicMock,
    actual: str,
    nuevo: str,
) -> None:
    propiedad = propiedad_existente(estado=actual)
    cambios = PropiedadAdminActualizar.model_validate({"estado": nuevo})
    repository.obtener_por_id.return_value = propiedad

    with pytest.raises(TransicionEstadoInvalidaError):
        service.actualizar_admin(propiedad.id, cambios)

    repository.actualizar.assert_not_called()
