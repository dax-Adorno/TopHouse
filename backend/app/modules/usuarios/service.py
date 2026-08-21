from app.modules.usuarios.models import Usuario
from app.modules.usuarios.passwords import (
    hashear_contrasena,
    verificar_contrasena,
)
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.usuarios.schemas import UsuarioCrear

HASH_FALSO = hashear_contrasena("TopHouse-hash-falso-no-utilizable")


class UsuarioService:
    def __init__(self, repository: UsuarioRepository) -> None:
        self.repository = repository

    def crear(self, datos: UsuarioCrear) -> Usuario:
        password_hash = hashear_contrasena(datos.contrasena)
        return self.repository.crear(datos, password_hash=password_hash)

    def autenticar(self, email: str, contrasena: str) -> Usuario | None:
        email_normalizado = email.strip().lower()
        usuario = self.repository.obtener_por_email(email_normalizado)

        if usuario is None:
            verificar_contrasena(contrasena, HASH_FALSO)
            return None

        contrasena_valida = verificar_contrasena(
            contrasena,
            usuario.password_hash,
        )
        if not contrasena_valida or not usuario.activo:
            return None

        return self.repository.registrar_ultimo_acceso(usuario)
