from io import BytesIO

import pytest
from PIL import Image

from app.modules.imagenes.constants import MAX_TAMANIO_IMAGEN_BYTES
from app.modules.imagenes.exceptions import (
    ImagenDemasiadoGrandeError,
    ImagenInvalidaError,
)
from app.modules.imagenes.processing import procesar_imagen


def crear_jpeg_con_exif() -> bytes:
    imagen = Image.new("RGB", (1200, 800), "blue")
    exif = Image.Exif()
    exif[274] = 6
    exif[315] = "Dato privado"
    salida = BytesIO()
    imagen.save(salida, format="JPEG", quality=90, exif=exif)
    return salida.getvalue()


def test_procesa_orientacion_webp_thumbnail_y_limpia_metadata() -> None:
    procesada = procesar_imagen(
        crear_jpeg_con_exif(),
        mime_type_declarado="image/jpeg",
    )

    assert (procesada.ancho, procesada.alto) == (800, 1200)
    assert procesada.mime_type_original == "image/jpeg"
    with Image.open(BytesIO(procesada.contenido_webp)) as imagen:
        assert imagen.format == "WEBP"
        assert imagen.getexif() == {}
        assert "xmp" not in imagen.info
    with Image.open(BytesIO(procesada.thumbnail_webp)) as thumbnail:
        assert thumbnail.format == "WEBP"
        assert thumbnail.width <= 480
        assert thumbnail.height <= 480


@pytest.mark.parametrize(
    "contenido",
    [b"no es una imagen", b""],
)
def test_rechaza_contenido_invalido(contenido: bytes) -> None:
    with pytest.raises(ImagenInvalidaError):
        procesar_imagen(contenido)


def test_rechaza_tipo_declarado_distinto_al_real() -> None:
    with pytest.raises(ImagenInvalidaError):
        procesar_imagen(
            crear_jpeg_con_exif(),
            mime_type_declarado="image/png",
        )


def test_rechaza_archivo_mayor_a_diez_mb() -> None:
    with pytest.raises(ImagenDemasiadoGrandeError):
        procesar_imagen(b"x" * (MAX_TAMANIO_IMAGEN_BYTES + 1))


def test_rechaza_dimensiones_menores_al_minimo() -> None:
    imagen = Image.new("RGB", (319, 500), "white")
    salida = BytesIO()
    imagen.save(salida, format="PNG")

    with pytest.raises(ImagenInvalidaError):
        procesar_imagen(salida.getvalue())
