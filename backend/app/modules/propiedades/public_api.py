from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.imagenes.dependencies import ImagenServiceDep
from app.modules.imagenes.models import ImagenPropiedad
from app.modules.imagenes.schemas import ImagenPublicaRespuesta
from app.modules.propiedades.dependencies import ServiceDep
from app.modules.propiedades.models import Propiedad
from app.modules.propiedades.schemas import (
    PaginaPropiedadesPublicas,
    PropiedadPublicaRespuesta,
    TipoOperacion,
)

router = APIRouter(
    prefix="/api/v1/publico/propiedades",
    tags=["Propiedades públicas"],
)


@router.get(
    "",
    response_model=PaginaPropiedadesPublicas,
)
def listar_propiedades_publicas(
    service: ServiceDep,
    imagen_service: ImagenServiceDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    tipo_operacion: TipoOperacion | None = None,
    tipo_propiedad: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    localidad: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    precio_min: Annotated[Decimal | None, Query(ge=0)] = None,
    precio_max: Annotated[Decimal | None, Query(ge=0)] = None,
    dormitorios_min: Annotated[int | None, Query(ge=0)] = None,
    destacada: bool | None = None,
) -> PaginaPropiedadesPublicas:
    if precio_min is not None and precio_max is not None and precio_min > precio_max:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="precio_min no puede superar precio_max",
        )

    propiedades, total = service.listar_publicadas(
        offset=offset,
        limit=limit,
        tipo_operacion=tipo_operacion,
        tipo_propiedad=tipo_propiedad,
        localidad=localidad,
        precio_min=precio_min,
        precio_max=precio_max,
        dormitorios_min=dormitorios_min,
        destacada=destacada,
    )
    imagenes_por_propiedad = imagen_service.listar_por_propiedades(
        [propiedad.id for propiedad in propiedades]
    )
    return PaginaPropiedadesPublicas(
        items=[
            _crear_respuesta_publica(
                propiedad,
                imagen_service,
                imagenes=imagenes_por_propiedad[propiedad.id],
            )
            for propiedad in propiedades
        ],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/{slug}",
    response_model=PropiedadPublicaRespuesta,
)
def obtener_propiedad_publica(
    slug: str,
    service: ServiceDep,
    imagen_service: ImagenServiceDep,
) -> PropiedadPublicaRespuesta:
    propiedad = service.obtener_publicada_por_slug(slug)
    return _crear_respuesta_publica(propiedad, imagen_service)


def _crear_respuesta_publica(
    propiedad: Propiedad,
    imagen_service: ImagenServiceDep,
    *,
    imagenes: list[ImagenPropiedad] | None = None,
) -> PropiedadPublicaRespuesta:
    modelos_imagen = (
        imagen_service.listar(propiedad.id) if imagenes is None else imagenes
    )
    respuestas_imagen = [imagen_service.respuesta(imagen) for imagen in modelos_imagen]
    datos = PropiedadPublicaRespuesta.model_validate(propiedad).model_dump()
    datos["imagenes"] = [
        ImagenPublicaRespuesta.model_validate(
            imagen.model_dump(
                include={
                    "id",
                    "url",
                    "url_thumbnail",
                    "ancho",
                    "alto",
                    "orden",
                    "es_portada",
                }
            )
        )
        for imagen in respuestas_imagen
    ]
    return PropiedadPublicaRespuesta.model_validate(datos)
