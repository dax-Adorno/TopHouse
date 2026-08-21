class ErrorPropiedad(Exception):
    """Error base del dominio de propiedades."""


class PropiedadDuplicadaError(ErrorPropiedad):
    """Una propiedad ya utiliza un valor que debe ser único."""

    def __init__(self, campo: str) -> None:
        self.campo = campo
        super().__init__(f"Ya existe una propiedad con el mismo {campo}")


class PersistenciaPropiedadError(ErrorPropiedad):
    """La base de datos rechazó una operación de persistencia."""


class PropiedadNoEncontradaError(ErrorPropiedad):
    """No existe una propiedad con el identificador solicitado."""


class TransicionEstadoInvalidaError(ErrorPropiedad):
    """El cambio de estado solicitado viola el flujo operativo."""

    def __init__(self, estado_actual: str, estado_nuevo: str) -> None:
        self.estado_actual = estado_actual
        self.estado_nuevo = estado_nuevo
        super().__init__(
            f"No se puede cambiar el estado de {estado_actual} a {estado_nuevo}"
        )


class GeneracionSlugError(ErrorPropiedad):
    """No fue posible generar un slug único para la propiedad."""
