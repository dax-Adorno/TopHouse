from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import settings
from app.core.health import comprobar_dependencias
from app.core.security import SecurityHeadersMiddleware
from app.modules.imagenes.api import router as imagenes_router
from app.modules.imagenes.handlers import registrar_manejadores_imagenes
from app.modules.propiedades.api import router as propiedades_router
from app.modules.propiedades.handlers import registrar_manejadores_propiedades
from app.modules.propiedades.public_api import router as propiedades_publicas_router
from app.modules.usuarios.api import router as usuarios_router

app = FastAPI(
    title="TopHouse API",
    description="API para la plataforma inmobiliaria TopHouse.",
    version="0.1.0",
    debug=settings.debug,
    docs_url=None if settings.is_production else "/docs",
    redoc_url=None if settings.is_production else "/redoc",
    openapi_url=None if settings.is_production else "/openapi.json",
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"],
    allow_headers=["Accept", "Content-Type", "X-CSRF-Token"],
)
app.add_middleware(SecurityHeadersMiddleware, production=settings.is_production)

app.include_router(propiedades_router)
app.include_router(propiedades_publicas_router)
app.include_router(usuarios_router)
app.include_router(imagenes_router)
registrar_manejadores_propiedades(app)
registrar_manejadores_imagenes(app)


@app.get(
    "/health",
    tags=["Health"],
    status_code=status.HTTP_200_OK,
)
def health_check() -> dict[str, str]:
    """
    Comprueba que la API se encuentra disponible.

    Este endpoint comprueba únicamente que el proceso responde.
    """
    return {
        "status": "ok",
        "service": "TopHouse API",
    }


@app.get(
    "/ready",
    tags=["Health"],
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_503_SERVICE_UNAVAILABLE: {}},
)
def readiness_check(response: Response) -> dict[str, object]:
    """Comprueba que PostgreSQL y el almacenamiento están disponibles."""
    checks = comprobar_dependencias()
    disponible = all(estado == "ok" for estado in checks.values())
    if not disponible:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return {
        "status": "ready" if disponible else "unavailable",
        "checks": checks,
    }
