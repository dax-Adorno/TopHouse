from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from app.modules.propiedades.dependencies import ServiceDep
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
    return PaginaPropiedadesPublicas(
        items=[
            PropiedadPublicaRespuesta.model_validate(propiedad)
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
) -> PropiedadPublicaRespuesta:
    propiedad = service.obtener_publicada_por_slug(slug)
    return PropiedadPublicaRespuesta.model_validate(propiedad)
