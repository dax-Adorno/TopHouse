import warnings
from dataclasses import dataclass
from io import BytesIO

from PIL import Image, ImageOps, UnidentifiedImageError

from app.modules.imagenes.constants import (
    MAX_DIMENSION_IMAGEN,
    MAX_TAMANIO_IMAGEN_BYTES,
    MIME_TYPES_PERMITIDOS,
    MIN_DIMENSION_IMAGEN,
)
from app.modules.imagenes.exceptions import (
    ImagenDemasiadoGrandeError,
    ImagenInvalidaError,
)

MIME_POR_FORMATO = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}
THUMBNAIL_MAXIMO = (480, 480)


@dataclass(frozen=True)
class ImagenProcesada:
    contenido_webp: bytes
    thumbnail_webp: bytes
    ancho: int
    alto: int
    mime_type_original: str
    tamanio_original: int


def procesar_imagen(
    contenido: bytes,
    *,
    mime_type_declarado: str | None = None,
) -> ImagenProcesada:
    tamanio = len(contenido)
    if tamanio == 0:
        raise ImagenInvalidaError("El archivo está vacío")
    if tamanio > MAX_TAMANIO_IMAGEN_BYTES:
        raise ImagenDemasiadoGrandeError("La imagen supera el límite de 10 MB")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(BytesIO(contenido)) as candidata:
                formato = candidata.format
                candidata.verify()

            mime_real = MIME_POR_FORMATO.get(formato or "")
            if mime_real not in MIME_TYPES_PERMITIDOS:
                raise ImagenInvalidaError("El formato real no está permitido")
            if (
                mime_type_declarado is not None
                and mime_type_declarado.lower() != mime_real
            ):
                raise ImagenInvalidaError(
                    "El tipo declarado no coincide con el contenido"
                )

            with Image.open(BytesIO(contenido)) as original:
                if getattr(original, "n_frames", 1) != 1:
                    raise ImagenInvalidaError("No se admiten imágenes animadas")
                original.load()
                normalizada = ImageOps.exif_transpose(original)
                _validar_dimensiones(normalizada.width, normalizada.height)
                preparada = _normalizar_modo(normalizada)
                contenido_webp = _guardar_webp(preparada, calidad=85)

                thumbnail = preparada.copy()
                thumbnail.thumbnail(THUMBNAIL_MAXIMO, Image.Resampling.LANCZOS)
                thumbnail_webp = _guardar_webp(thumbnail, calidad=80)
    except ImagenInvalidaError:
        raise
    except (
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
        UnidentifiedImageError,
        OSError,
        SyntaxError,
        ValueError,
    ) as error:
        raise ImagenInvalidaError("El contenido no es una imagen válida") from error

    return ImagenProcesada(
        contenido_webp=contenido_webp,
        thumbnail_webp=thumbnail_webp,
        ancho=preparada.width,
        alto=preparada.height,
        mime_type_original=mime_real,
        tamanio_original=tamanio,
    )


def _validar_dimensiones(ancho: int, alto: int) -> None:
    if not (
        MIN_DIMENSION_IMAGEN <= ancho <= MAX_DIMENSION_IMAGEN
        and MIN_DIMENSION_IMAGEN <= alto <= MAX_DIMENSION_IMAGEN
    ):
        raise ImagenInvalidaError(
            "Las dimensiones deben estar entre 320 y 12000 píxeles"
        )


def _normalizar_modo(imagen: Image.Image) -> Image.Image:
    if imagen.mode in {"RGBA", "LA"} or "transparency" in imagen.info:
        return imagen.convert("RGBA")
    return imagen.convert("RGB")


def _guardar_webp(imagen: Image.Image, *, calidad: int) -> bytes:
    salida = BytesIO()
    imagen.save(
        salida,
        format="WEBP",
        quality=calidad,
        method=6,
    )
    return salida.getvalue()
