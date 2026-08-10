from fastapi import FastAPI, status

app = FastAPI(
    title="TopHouse API",
    description="API para la plataforma inmobiliaria TopHouse.",
    version="0.1.0",
)


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
