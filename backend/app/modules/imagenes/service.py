import logging
from pathlib import Path
from uuid import uuid4

from app.modules.imagenes.constants import MAX_IMAGENES_POR_PROPIEDAD
from app.modules.imagenes.exceptions import LimiteImagenesError
from app.modules.imagenes.models import ImagenPropiedad
from app.modules.imagenes.processing import procesar_imagen
from app.modules.imagenes.repository import ImagenRepository
from app.modules.imagenes.schemas import ImagenMetadatosCrear
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
