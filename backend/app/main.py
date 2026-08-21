from fastapi import FastAPI, status

from app.modules.propiedades.api import router as propiedades_router
from app.modules.propiedades.handlers import registrar_manejadores_propiedades
from app.modules.propiedades.public_api import router as propiedades_publicas_router

app = FastAPI(
    title="TopHouse API",
    description="API para la plataforma inmobiliaria TopHouse.",
    version="0.1.0",
)

app.include_router(propiedades_router)
app.include_router(propiedades_publicas_router)
registrar_manejadores_propiedades(app)


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
