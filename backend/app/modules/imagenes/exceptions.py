class ImagenInvalidaError(ValueError):
    """El contenido recibido no es una imagen segura o permitida."""


class ImagenDemasiadoGrandeError(ImagenInvalidaError):
    """El archivo supera el límite de bytes permitido."""
