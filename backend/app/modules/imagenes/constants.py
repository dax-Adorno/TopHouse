MAX_IMAGENES_POR_PROPIEDAD = 20
MAX_TAMANIO_IMAGEN_BYTES = 10 * 1024 * 1024
MIN_DIMENSION_IMAGEN = 320
MAX_DIMENSION_IMAGEN = 12_000

MIME_TYPES_PERMITIDOS = frozenset(
    {
        "image/jpeg",
        "image/png",
        "image/webp",
    }
)
