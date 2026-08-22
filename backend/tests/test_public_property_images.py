from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast

from app.modules.imagenes.models import ImagenPropiedad
from app.modules.imagenes.schemas import ImagenApiRespuesta
from app.modules.imagenes.service import ImagenService
from app.modules.propiedades.models import Propiedad
from app.modules.propiedades.public_api import _crear_respuesta_publica


class ImagenServiceFalso:
    def listar(self, propiedad_id: int) -> list[ImagenPropiedad]:
        assert propiedad_id == 7
        return [cast(ImagenPropiedad, SimpleNamespace(id=3))]

    def respuesta(self, _imagen: ImagenPropiedad) -> ImagenApiRespuesta:
        return ImagenApiRespuesta(
            id=3,
            propiedad_id=7,
            nombre_original="fachada.jpg",
            mime_type="image/jpeg",
            tamanio_bytes=1000,
            ancho=1200,
            alto=800,
            orden=0,
            es_portada=True,
            creado_en=datetime.now(UTC),
            url="https://storage.example/fachada",
            url_thumbnail="https://storage.example/fachada-thumb",
        )


def test_respuesta_publica_incluye_galeria_sin_metadatos_internos() -> None:
    ahora = datetime.now(UTC)
    propiedad = Propiedad(
        id=7,
        codigo="PUB-7",
        slug="propiedad-publica",
        titulo="Propiedad pública",
        descripcion="Descripción",
        tipo_operacion="venta",
        tipo_propiedad="casa",
        precio=None,
        moneda=None,
        localidad="Asunción",
        zona=None,
        dormitorios=None,
        banios=None,
        superficie_cubierta=None,
        superficie_total=None,
        estado="publicada",
        destacada=True,
        creado_en=ahora,
        actualizado_en=ahora,
    )

    respuesta = _crear_respuesta_publica(
        propiedad,
        cast(ImagenService, ImagenServiceFalso()),
    )
    imagen = respuesta.model_dump()["imagenes"][0]

    assert imagen["es_portada"] is True
    assert imagen["url"].startswith("https://")
    assert "nombre_original" not in imagen
    assert "mime_type" not in imagen
    assert "clave_objeto" not in imagen
