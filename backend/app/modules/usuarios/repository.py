from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.usuarios.exceptions import (
    PersistenciaUsuarioError,
    UsuarioDuplicadoError,
)
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.schemas import UsuarioCrear


class UsuarioRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, datos: UsuarioCrear, *, password_hash: str) -> Usuario:
        email = str(datos.email).lower()
        if self.obtener_por_email(email) is not None:
            raise UsuarioDuplicadoError("Ya existe un usuario con ese email")

        usuario = Usuario(
            email=email,
            nombre=datos.nombre,
            password_hash=password_hash,
            rol=datos.rol,
        )
        self.session.add(usuario)
        self._confirmar()
        self.session.refresh(usuario)
        return usuario

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        return self.session.get(Usuario, usuario_id)

    def obtener_por_email(self, email: str) -> Usuario | None:
        consulta = select(Usuario).where(Usuario.email == email.lower())
        return self.session.scalar(consulta)

    def registrar_ultimo_acceso(self, usuario: Usuario) -> Usuario:
        usuario.ultimo_acceso_en = datetime.now(UTC)
        self._confirmar()
        self.session.refresh(usuario)
        return usuario

    def _confirmar(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            constraint = getattr(
                getattr(error.orig, "diag", None),
                "constraint_name",
                "",
            )
            if constraint and "email" in constraint:
                raise UsuarioDuplicadoError(
                    "Ya existe un usuario con ese email"
                ) from error
            raise PersistenciaUsuarioError(
                "La base de datos rechazó la operación"
            ) from error
