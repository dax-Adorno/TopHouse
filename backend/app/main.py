from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
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
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    Este endpoint no consulta todavía la base de datos.
    """
    return {
        "status": "ok",
        "service": "TopHouse API",
    }
