from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.modules.propiedades.exceptions import (
    GeneracionSlugError,
    PersistenciaPropiedadError,
    PropiedadDuplicadaError,
    PropiedadNoEncontradaError,
    TransicionEstadoInvalidaError,
)


def registrar_manejadores_propiedades(app: FastAPI) -> None:
    @app.exception_handler(PropiedadNoEncontradaError)
    async def propiedad_no_encontrada(
        _request: Request,
        error: PropiedadNoEncontradaError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(error)},
        )

    @app.exception_handler(PropiedadDuplicadaError)
    async def propiedad_duplicada(
        _request: Request,
        error: PropiedadDuplicadaError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"detail": str(error), "campo": error.campo},
        )

    @app.exception_handler(TransicionEstadoInvalidaError)
    async def transicion_invalida(
        _request: Request,
        error: TransicionEstadoInvalidaError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": str(error),
                "estado_actual": error.estado_actual,
                "estado_nuevo": error.estado_nuevo,
            },
        )

    @app.exception_handler(PersistenciaPropiedadError)
    @app.exception_handler(GeneracionSlugError)
    async def error_interno_propiedad(
        _request: Request,
        _error: PersistenciaPropiedadError | GeneracionSlugError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "No fue posible procesar la propiedad"},
        )
