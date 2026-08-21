from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.modules.imagenes.exceptions import (
    AlmacenamientoImagenError,
    ImagenInvalidaError,
    ImagenNoEncontradaError,
    LimiteImagenesError,
    OrdenImagenesInvalidoError,
)


def registrar_manejadores_imagenes(app: FastAPI) -> None:
    @app.exception_handler(ImagenNoEncontradaError)
    async def imagen_no_encontrada(
        _request: Request,
        error: ImagenNoEncontradaError,
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(error)})

    @app.exception_handler(ImagenInvalidaError)
    async def imagen_invalida(
        _request: Request,
        error: ImagenInvalidaError,
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(error)})

    @app.exception_handler(LimiteImagenesError)
    @app.exception_handler(OrdenImagenesInvalidoError)
    async def conflicto_imagen(
        _request: Request,
        error: LimiteImagenesError | OrdenImagenesInvalidoError,
    ) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": str(error)})

    @app.exception_handler(AlmacenamientoImagenError)
    async def almacenamiento_no_disponible(
        _request: Request,
        _error: AlmacenamientoImagenError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Almacenamiento de imágenes no disponible"},
        )
