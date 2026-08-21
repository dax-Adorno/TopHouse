from datetime import timedelta
from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, status

from app.core.config import settings
from app.core.dependencies import SessionDep
from app.modules.usuarios.models import SesionUsuario, Usuario
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.usuarios.service import UsuarioService
from app.modules.usuarios.sessions import SesionRepository, SesionService

SESSION_COOKIE = "tophouse_session"
CSRF_COOKIE = "tophouse_csrf"


def obtener_sesion_service(session: SessionDep) -> SesionService:
    return SesionService(
        UsuarioService(UsuarioRepository(session)),
        SesionRepository(session),
        duracion=timedelta(hours=settings.session_duration_hours),
    )


SesionServiceDep = Annotated[SesionService, Depends(obtener_sesion_service)]


def obtener_autenticacion(
    service: SesionServiceDep,
    token: Annotated[str | None, Cookie(alias=SESSION_COOKIE)] = None,
) -> tuple[SesionUsuario, Usuario]:
    autenticacion = service.autenticar(token) if token else None
    if autenticacion is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida",
        )
    return autenticacion


AutenticacionDep = Annotated[
    tuple[SesionUsuario, Usuario],
    Depends(obtener_autenticacion),
]


def verificar_csrf(
    autenticacion: AutenticacionDep,
    service: SesionServiceDep,
    csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> tuple[SesionUsuario, Usuario]:
    sesion, _usuario = autenticacion
    if csrf_token is None or not service.csrf_valido(sesion, csrf_token):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token CSRF inválido",
        )
    return autenticacion


CsrfDep = Annotated[tuple[SesionUsuario, Usuario], Depends(verificar_csrf)]


def requerir_administrador(
    autenticacion: CsrfDep,
) -> tuple[SesionUsuario, Usuario]:
    _sesion, usuario = autenticacion
    if usuario.rol != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador",
        )
    return autenticacion


AdminCsrfDep = Annotated[
    tuple[SesionUsuario, Usuario],
    Depends(requerir_administrador),
]
