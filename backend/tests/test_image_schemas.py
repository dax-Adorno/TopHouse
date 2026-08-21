import pytest
from pydantic import ValidationError

from app.modules.imagenes.constants import MAX_TAMANIO_IMAGEN_BYTES
from app.modules.imagenes.schemas import ImagenMetadatosCrear, ImagenOrdenActualizar


def metadatos_validos() -> dict[str, object]:
    return {
        "clave_objeto": "propiedades/1/imagen.webp",
        "clave_thumbnail": "propiedades/1/imagen-thumb.webp",
        "nombre_original": "fachada.jpg",
        "mime_type": "image/jpeg",
        "tamanio_bytes": 500_000,
        "ancho": 1600,
        "alto": 1200,
        "orden": 0,
    }


def test_metadatos_aceptan_imagen_valida() -> None:
    imagen = ImagenMetadatosCrear.model_validate(metadatos_validos())
    assert imagen.mime_type == "image/jpeg"
    assert imagen.es_portada is False


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("mime_type", "image/svg+xml"),
        ("tamanio_bytes", MAX_TAMANIO_IMAGEN_BYTES + 1),
        ("ancho", 319),
        ("alto", 12_001),
        ("orden", -1),
    ],
)
def test_metadatos_rechazan_archivos_fuera_de_limites(
    campo: str,
    valor: object,
) -> None:
    datos = {**metadatos_validos(), campo: valor}
    with pytest.raises(ValidationError):
        ImagenMetadatosCrear.model_validate(datos)


def test_orden_rechaza_ids_duplicados() -> None:
    with pytest.raises(ValidationError):
        ImagenOrdenActualizar(imagen_ids=[1, 2, 1])
