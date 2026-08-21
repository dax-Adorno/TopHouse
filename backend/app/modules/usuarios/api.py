from datetime import datetime

from fastapi import APIRouter, HTTPException, Response, status

from app.core.config import settings
from app.modules.usuarios.dependencies import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    AutenticacionDep,
    CsrfDep,
    SesionServiceDep,
)
from app.modules.usuarios.schemas import LoginSolicitud, UsuarioRespuesta

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticación"])


def _configurar_cookie(
    response: Response,
    *,
    nombre: str,
    valor: str,
    expira_en: datetime,
    httponly: bool,
) -> None:
    response.set_cookie(
        key=nombre,
        value=valor,
        expires=expira_en,
        httponly=httponly,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )


@router.post("/login", response_model=UsuarioRespuesta)
def login(
    datos: LoginSolicitud,
    response: Response,
    service: SesionServiceDep,
) -> UsuarioRespuesta:
    credenciales = service.iniciar(str(datos.email), datos.contrasena)
    if credenciales is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    _configurar_cookie(
        response,
        nombre=SESSION_COOKIE,
        valor=credenciales.token,
        expira_en=credenciales.expira_en,
        httponly=True,
    )
    _configurar_cookie(
        response,
        nombre=CSRF_COOKIE,
        valor=credenciales.csrf_token,
        expira_en=credenciales.expira_en,
        httponly=False,
    )
    return UsuarioRespuesta.model_validate(credenciales.usuario)


@router.get("/me", response_model=UsuarioRespuesta)
def usuario_actual(autenticacion: AutenticacionDep) -> UsuarioRespuesta:
    _sesion, usuario = autenticacion
    return UsuarioRespuesta.model_validate(usuario)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    autenticacion: CsrfDep,
    service: SesionServiceDep,
) -> None:
    sesion, _usuario = autenticacion
    service.cerrar(sesion)
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")
