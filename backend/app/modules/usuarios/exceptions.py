class ErrorUsuario(Exception):
    """Error base del dominio de usuarios."""


class UsuarioDuplicadoError(ErrorUsuario):
    """Ya existe un usuario con el mismo email."""


class PersistenciaUsuarioError(ErrorUsuario):
    """La base de datos rechazó una operación sobre usuarios."""
