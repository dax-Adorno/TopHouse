from io import BytesIO
from types import SimpleNamespace

import pytest
from PIL import Image

from app.modules.imagenes.constants import MAX_IMAGENES_POR_PROPIEDAD
from app.modules.imagenes.exceptions import (
    AlmacenamientoImagenError,
    LimiteImagenesError,
)
from app.modules.imagenes.service import ImagenService


def imagen_jpeg() -> bytes:
    imagen = Image.new("RGB", (800, 600), "green")
    salida = BytesIO()
    imagen.save(salida, format="JPEG")
    return salida.getvalue()


class RepositoryFalso:
    def __init__(self, cantidad: int = 0) -> None:
        self.cantidad = cantidad
        self.datos_creados = None

    def contar(self, _propiedad_id: int) -> int:
        return self.cantidad

    def siguiente_orden(self, _propiedad_id: int) -> int:
        return self.cantidad

    def crear(self, propiedad_id: int, datos: object) -> object:
        self.datos_creados = datos
        return SimpleNamespace(id=1, propiedad_id=propiedad_id, **datos.model_dump())


class PropiedadServiceFalso:
    def obtener_por_id(self, propiedad_id: int) -> object:
        return SimpleNamespace(id=propiedad_id)


class AlmacenamientoFalso:
    def __init__(self, *, fallar_en: int | None = None) -> None:
        self.guardadas: list[str] = []
        self.eliminadas: list[str] = []
        self.fallar_en = fallar_en

    def guardar(self, clave: str, _contenido: bytes, *, content_type: str) -> None:
        assert content_type == "image/webp"
        if self.fallar_en == len(self.guardadas) + 1:
            raise AlmacenamientoImagenError("fallo simulado")
        self.guardadas.append(clave)

    def eliminar(self, clave: str) -> None:
        self.eliminadas.append(clave)


def crear_service(
    repository: RepositoryFalso,
    almacenamiento: AlmacenamientoFalso,
) -> ImagenService:
    return ImagenService(repository, PropiedadServiceFalso(), almacenamiento)


def test_agrega_webp_thumbnail_y_primera_portada() -> None:
    repository = RepositoryFalso()
    almacenamiento = AlmacenamientoFalso()

    imagen = crear_service(repository, almacenamiento).agregar(
        propiedad_id=7,
        nombre_original="../fachada.jpg",
        contenido=imagen_jpeg(),
        mime_type_declarado="image/jpeg",
    )

    assert len(almacenamiento.guardadas) == 2
    assert all(clave.startswith("propiedades/7/") for clave in almacenamiento.guardadas)
    assert imagen.nombre_original == "fachada.jpg"
    assert imagen.es_portada is True
    assert imagen.orden == 0


def test_rechaza_propiedad_con_limite_antes_de_guardar() -> None:
    almacenamiento = AlmacenamientoFalso()
    service = crear_service(
        RepositoryFalso(MAX_IMAGENES_POR_PROPIEDAD),
        almacenamiento,
    )

    with pytest.raises(LimiteImagenesError):
        service.agregar(
            propiedad_id=7,
            nombre_original="fachada.jpg",
            contenido=imagen_jpeg(),
            mime_type_declarado="image/jpeg",
        )
    assert almacenamiento.guardadas == []


def test_limpia_primer_objeto_si_falla_el_segundo() -> None:
    almacenamiento = AlmacenamientoFalso(fallar_en=2)
    service = crear_service(RepositoryFalso(), almacenamiento)

    with pytest.raises(AlmacenamientoImagenError):
        service.agregar(
            propiedad_id=7,
            nombre_original="fachada.jpg",
            contenido=imagen_jpeg(),
            mime_type_declarado="image/jpeg",
        )
    assert almacenamiento.eliminadas == almacenamiento.guardadas
