from datetime import UTC, datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.propiedades.schemas import (
    EstadoPropiedad,
    PropiedadActualizar,
    PropiedadAdminActualizar,
    PropiedadAdminRespuesta,
    PropiedadCrear,
    PropiedadPublicaRespuesta,
    TipoOperacion,
)


def datos_propiedad(**cambios: object) -> dict[str, object]:
    datos: dict[str, object] = {
        "codigo": "TH-001",
        "titulo": "Casa céntrica",
        "descripcion": "Propiedad lista para habitar",
        "tipo_operacion": "venta",
        "tipo_propiedad": "casa",
        "precio": "150000.00",
        "moneda": "USD",
        "localidad": "Merlo",
    }
    datos.update(cambios)
    return datos


def datos_respuesta(**cambios: object) -> dict[str, object]:
    ahora = datetime.now(UTC)
    datos = datos_propiedad(
        id=1,
        slug="casa-centrica",
        estado="publicada",
        destacada=False,
        creado_en=ahora,
        actualizado_en=ahora,
    )
    datos.update(cambios)
    return datos


def test_propiedad_crear_aplica_defaults_seguros() -> None:
    propiedad = PropiedadCrear.model_validate(datos_propiedad())

    assert propiedad.tipo_operacion is TipoOperacion.VENTA
    assert propiedad.precio == Decimal("150000.00")
    assert propiedad.mostrar_ubicacion_exacta is False
    assert propiedad.latitud is None
    assert propiedad.longitud is None


@pytest.mark.parametrize(
    "campo",
    ["id", "slug", "estado", "destacada", "creado_en", "actualizado_en"],
)
def test_propiedad_crear_rechaza_campos_controlados_por_backend(campo: str) -> None:
    with pytest.raises(ValidationError):
        PropiedadCrear.model_validate(datos_propiedad(**{campo: "no permitido"}))


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("tipo_operacion", "permuta"),
        ("precio", -1),
        ("dormitorios", -1),
        ("banios", -1),
        ("superficie_total", -1),
        ("moneda", "US"),
        ("latitud", 91),
        ("longitud", -181),
    ],
)
def test_propiedad_crear_rechaza_valores_invalidos(campo: str, valor: object) -> None:
    datos = datos_propiedad(latitud=-32.34, longitud=-65.01)
    datos[campo] = valor

    with pytest.raises(ValidationError):
        PropiedadCrear.model_validate(datos)


def test_propiedad_crear_requiere_coordenadas_completas() -> None:
    with pytest.raises(ValidationError, match="deben enviarse juntas"):
        PropiedadCrear.model_validate(datos_propiedad(latitud=-32.34))


def test_propiedad_actualizar_acepta_patch_parcial() -> None:
    actualizacion = PropiedadActualizar.model_validate({"titulo": "Nuevo título"})

    assert actualizacion.model_dump(exclude_unset=True) == {"titulo": "Nuevo título"}


@pytest.mark.parametrize(
    "datos",
    [
        {"latitud": -25.30},
        {"longitud": -57.63},
        {"latitud": None},
        {"longitud": None},
    ],
)
def test_propiedad_actualizar_requiere_par_de_coordenadas(
    datos: dict[str, object],
) -> None:
    with pytest.raises(ValidationError, match="deben actualizarse juntas"):
        PropiedadActualizar.model_validate(datos)


def test_propiedad_actualizar_permite_borrar_ambas_coordenadas() -> None:
    actualizacion = PropiedadActualizar.model_validate(
        {"latitud": None, "longitud": None}
    )

    assert actualizacion.model_dump(exclude_unset=True) == {
        "latitud": None,
        "longitud": None,
    }


def test_actualizacion_comun_rechaza_estado_y_destacada() -> None:
    with pytest.raises(ValidationError):
        PropiedadActualizar.model_validate({"estado": "publicada", "destacada": True})


def test_actualizacion_admin_permite_estado_y_destacada() -> None:
    actualizacion = PropiedadAdminActualizar.model_validate(
        {"estado": "publicada", "destacada": True}
    )

    assert actualizacion.estado is EstadoPropiedad.PUBLICADA
    assert actualizacion.destacada is True


def test_respuesta_admin_incluye_ubicacion_exacta() -> None:
    respuesta = PropiedadAdminRespuesta.model_validate(
        datos_respuesta(
            direccion="Av. Principal 123",
            latitud=-32.34,
            longitud=-65.01,
            mostrar_ubicacion_exacta=False,
        )
    )

    assert respuesta.direccion == "Av. Principal 123"
    assert respuesta.latitud == Decimal("-32.34")


def test_respuesta_publica_excluye_datos_de_ubicacion_exacta() -> None:
    respuesta = PropiedadPublicaRespuesta.model_validate(
        datos_respuesta(
            direccion="Av. Principal 123",
            latitud=-32.34,
            longitud=-65.01,
            mostrar_ubicacion_exacta=True,
        )
    )
    datos_publicos = respuesta.model_dump()

    assert "direccion" not in datos_publicos
    assert "latitud" not in datos_publicos
    assert "longitud" not in datos_publicos
    assert "mostrar_ubicacion_exacta" not in datos_publicos
