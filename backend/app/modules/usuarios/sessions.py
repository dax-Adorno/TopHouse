from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from hmac import compare_digest
from secrets import token_urlsafe

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.usuarios.models import SesionUsuario, Usuario
from app.modules.usuarios.service import UsuarioService


def resumir_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class CredencialesSesion:
    token: str
    csrf_token: str
    expira_en: datetime
    usuario: Usuario


class SesionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(
        self,
        *,
        usuario_id: int,
        token_hash: str,
        csrf_token_hash: str,
        expira_en: datetime,
    ) -> SesionUsuario:
        sesion = SesionUsuario(
            usuario_id=usuario_id,
            token_hash=token_hash,
            csrf_token_hash=csrf_token_hash,
            expira_en=expira_en,
        )
        self.session.add(sesion)
        self.session.commit()
        self.session.refresh(sesion)
        return sesion

    def obtener_activa(self, token_hash: str) -> SesionUsuario | None:
        ahora = datetime.now(UTC)
        consulta = select(SesionUsuario).where(
            SesionUsuario.token_hash == token_hash,
            SesionUsuario.revocada_en.is_(None),
            SesionUsuario.expira_en > ahora,
        )
        return self.session.scalar(consulta)

    def obtener_usuario(self, usuario_id: int) -> Usuario | None:
        return self.session.get(Usuario, usuario_id)

    def revocar(self, sesion: SesionUsuario) -> None:
        sesion.revocada_en = datetime.now(UTC)
        self.session.commit()


class SesionService:
    def __init__(
        self,
        usuario_service: UsuarioService,
        repository: SesionRepository,
        *,
        duracion: timedelta,
    ) -> None:
        self.usuario_service = usuario_service
        self.repository = repository
        self.duracion = duracion

    def iniciar(self, email: str, contrasena: str) -> CredencialesSesion | None:
        usuario = self.usuario_service.autenticar(email, contrasena)
        if usuario is None:
            return None

        token = token_urlsafe(32)
        csrf_token = token_urlsafe(32)
        expira_en = datetime.now(UTC) + self.duracion
        self.repository.crear(
            usuario_id=usuario.id,
            token_hash=resumir_token(token),
            csrf_token_hash=resumir_token(csrf_token),
            expira_en=expira_en,
        )
        return CredencialesSesion(token, csrf_token, expira_en, usuario)

    def autenticar(self, token: str) -> tuple[SesionUsuario, Usuario] | None:
        sesion = self.repository.obtener_activa(resumir_token(token))
        if sesion is None:
            return None
        usuario = self.repository.obtener_usuario(sesion.usuario_id)
        if usuario is None or not usuario.activo:
            return None
        return sesion, usuario

    def csrf_valido(self, sesion: SesionUsuario, csrf_token: str) -> bool:
        return compare_digest(
            sesion.csrf_token_hash,
            resumir_token(csrf_token),
        )

    def cerrar(self, sesion: SesionUsuario) -> None:
        self.repository.revocar(sesion)
