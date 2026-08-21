import logging
from pathlib import Path
from uuid import uuid4

from app.modules.imagenes.constants import MAX_IMAGENES_POR_PROPIEDAD
from app.modules.imagenes.exceptions import (
    ImagenNoEncontradaError,
    LimiteImagenesError,
    OrdenImagenesInvalidoError,
)
from app.modules.imagenes.models import ImagenPropiedad
from app.modules.imagenes.processing import procesar_imagen
from app.modules.imagenes.repository import ImagenRepository
from app.modules.imagenes.schemas import (
    ImagenApiRespuesta,
    ImagenMetadatosCrear,
    ImagenRespuesta,
)
from app.modules.imagenes.storage import AlmacenamientoImagenes
from app.modules.propiedades.service import PropiedadService

logger = logging.getLogger(__name__)


class ImagenService:
    def __init__(
        self,
        repository: ImagenRepository,
        propiedad_service: PropiedadService,
        almacenamiento: AlmacenamientoImagenes,
    ) -> None:
        self.repository = repository
        self.propiedad_service = propiedad_service
        self.almacenamiento = almacenamiento

    def agregar(
        self,
        *,
        propiedad_id: int,
        nombre_original: str,
        contenido: bytes,
        mime_type_declarado: str | None,
    ) -> ImagenPropiedad:
        self.propiedad_service.obtener_por_id(propiedad_id)
        if self.repository.contar(propiedad_id) >= MAX_IMAGENES_POR_PROPIEDAD:
            raise LimiteImagenesError("La propiedad admite hasta 20 imágenes")

        procesada = procesar_imagen(
            contenido,
            mime_type_declarado=mime_type_declarado,
        )
        identificador = uuid4().hex
        base = f"propiedades/{propiedad_id}/{identificador}"
        clave_objeto = f"{base}.webp"
        clave_thumbnail = f"{base}-thumb.webp"
        guardadas: list[str] = []
        try:
            self.almacenamiento.guardar(
                clave_objeto,
                procesada.contenido_webp,
                content_type="image/webp",
            )
            guardadas.append(clave_objeto)
            self.almacenamiento.guardar(
                clave_thumbnail,
                procesada.thumbnail_webp,
                content_type="image/webp",
            )
            guardadas.append(clave_thumbnail)
            return self.repository.crear(
                propiedad_id,
                ImagenMetadatosCrear(
                    clave_objeto=clave_objeto,
                    clave_thumbnail=clave_thumbnail,
                    nombre_original=Path(nombre_original).name,
                    mime_type=procesada.mime_type_original,
                    tamanio_bytes=procesada.tamanio_original,
                    ancho=procesada.ancho,
                    alto=procesada.alto,
                    orden=self.repository.siguiente_orden(propiedad_id),
                    es_portada=self.repository.contar(propiedad_id) == 0,
                ),
            )
        except Exception:
            for clave in reversed(guardadas):
                try:
                    self.almacenamiento.eliminar(clave)
                except Exception:
                    logger.exception(
                        "Falló la limpieza compensatoria del objeto %s",
                        clave,
                    )
            raise

    def listar(self, propiedad_id: int) -> list[ImagenPropiedad]:
        self.propiedad_service.obtener_por_id(propiedad_id)
        return self.repository.listar(propiedad_id)

    def obtener(self, propiedad_id: int, imagen_id: int) -> ImagenPropiedad:
        imagen = self.repository.obtener(imagen_id)
        if imagen is None or imagen.propiedad_id != propiedad_id:
            raise ImagenNoEncontradaError("No existe la imagen en esa propiedad")
        return imagen

    def reordenar(
        self,
        propiedad_id: int,
        imagen_ids: list[int],
    ) -> list[ImagenPropiedad]:
        imagenes = self.listar(propiedad_id)
        por_id = {imagen.id: imagen for imagen in imagenes}
        if set(imagen_ids) != set(por_id) or len(imagen_ids) != len(imagenes):
            raise OrdenImagenesInvalidoError(
                "Deben enviarse todas las imágenes de la propiedad una sola vez"
            )
        ordenadas = [por_id[imagen_id] for imagen_id in imagen_ids]
        self.repository.reordenar(ordenadas)
        return ordenadas

    def establecer_portada(
        self,
        propiedad_id: int,
        imagen_id: int,
    ) -> ImagenPropiedad:
        portada = self.obtener(propiedad_id, imagen_id)
        imagenes = self.repository.listar(propiedad_id)
        self.repository.establecer_portada(imagenes, portada)
        return portada

    def eliminar(self, propiedad_id: int, imagen_id: int) -> None:
        imagen = self.obtener(propiedad_id, imagen_id)
        era_portada = imagen.es_portada
        self.almacenamiento.eliminar(imagen.clave_objeto)
        self.almacenamiento.eliminar(imagen.clave_thumbnail)
        self.repository.eliminar(imagen)
        restantes = self.repository.listar(propiedad_id)
        if era_portada and restantes:
            self.repository.establecer_portada(restantes, restantes[0])

    def respuesta(self, imagen: ImagenPropiedad) -> ImagenApiRespuesta:
        datos = ImagenRespuesta.model_validate(imagen).model_dump()
        return ImagenApiRespuesta(
            **datos,
            url=self.almacenamiento.obtener_url(imagen.clave_objeto),
            url_thumbnail=self.almacenamiento.obtener_url(imagen.clave_thumbnail),
        )
