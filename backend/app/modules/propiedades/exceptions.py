class ErrorPropiedad(Exception):
    """Error base del dominio de propiedades."""


class PropiedadDuplicadaError(ErrorPropiedad):
    """Una propiedad ya utiliza un valor que debe ser único."""

    def __init__(self, campo: str) -> None:
        self.campo = campo
        super().__init__(f"Ya existe una propiedad con el mismo {campo}")


class PersistenciaPropiedadError(ErrorPropiedad):
    """La base de datos rechazó una operación de persistencia."""
