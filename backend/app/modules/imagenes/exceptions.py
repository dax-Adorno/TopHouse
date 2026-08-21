class ImagenInvalidaError(ValueError):
    """El contenido recibido no es una imagen segura o permitida."""


class ImagenDemasiadoGrandeError(ImagenInvalidaError):
    """El archivo supera el límite de bytes permitido."""


class LimiteImagenesError(ValueError):
    """La propiedad ya alcanzó la cantidad máxima de imágenes."""


class AlmacenamientoImagenError(RuntimeError):
    """El almacenamiento externo no pudo completar una operación."""
