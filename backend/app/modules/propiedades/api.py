from fastapi import APIRouter, Depends, Query, status

from app.modules.propiedades.dependencies import ServiceDep
from app.modules.propiedades.schemas import (
    PaginaPropiedadesAdmin,
    PropiedadActualizar,
    PropiedadAdminActualizar,
    PropiedadAdminRespuesta,
    PropiedadCrear,
)
from app.modules.usuarios.audit import AuditoriaDep
from app.modules.usuarios.dependencies import (
    AdminCsrfDep,
    CsrfDep,
    obtener_autenticacion,
)

router = APIRouter(
    prefix="/api/v1/propiedades",
    tags=["Propiedades"],
    dependencies=[Depends(obtener_autenticacion)],
)


@router.post(
    "",
    response_model=PropiedadAdminRespuesta,
    status_code=status.HTTP_201_CREATED,
)
def crear_propiedad(
    datos: PropiedadCrear,
    service: ServiceDep,
    autenticacion: CsrfDep,
    auditoria: AuditoriaDep,
) -> PropiedadAdminRespuesta:
    propiedad = service.crear(datos)
    _sesion, usuario = autenticacion
    auditoria.registrar(
        usuario=usuario,
        accion="propiedad.creada",
        recurso="propiedad",
        recurso_id=propiedad.id,
        detalles={"codigo": propiedad.codigo},
    )
    return PropiedadAdminRespuesta.model_validate(propiedad)


@router.get(
    "",
    response_model=PaginaPropiedadesAdmin,
)
def listar_propiedades(
    service: ServiceDep,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> PaginaPropiedadesAdmin:
    propiedades, total = service.listar(offset=offset, limit=limit)
    return PaginaPropiedadesAdmin(
        items=[
            PropiedadAdminRespuesta.model_validate(propiedad)
            for propiedad in propiedades
        ],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get(
    "/slug/{slug}",
    response_model=PropiedadAdminRespuesta,
)
def obtener_propiedad_por_slug(
    slug: str,
    service: ServiceDep,
) -> PropiedadAdminRespuesta:
    propiedad = service.obtener_por_slug(slug)
    return PropiedadAdminRespuesta.model_validate(propiedad)


@router.get(
    "/{propiedad_id}",
    response_model=PropiedadAdminRespuesta,
)
def obtener_propiedad(
    propiedad_id: int,
    service: ServiceDep,
) -> PropiedadAdminRespuesta:
    propiedad = service.obtener_por_id(propiedad_id)
    return PropiedadAdminRespuesta.model_validate(propiedad)


@router.patch(
    "/{propiedad_id}",
    response_model=PropiedadAdminRespuesta,
)
def actualizar_propiedad(
    propiedad_id: int,
    cambios: PropiedadActualizar,
    service: ServiceDep,
    autenticacion: CsrfDep,
    auditoria: AuditoriaDep,
) -> PropiedadAdminRespuesta:
    propiedad = service.actualizar(propiedad_id, cambios)
    _sesion, usuario = autenticacion
    auditoria.registrar(
        usuario=usuario,
        accion="propiedad.actualizada",
        recurso="propiedad",
        recurso_id=propiedad.id,
        detalles=cambios.model_dump(exclude_unset=True, mode="json"),
    )
    return PropiedadAdminRespuesta.model_validate(propiedad)


@router.patch(
    "/{propiedad_id}/admin",
    response_model=PropiedadAdminRespuesta,
)
def actualizar_propiedad_admin(
    propiedad_id: int,
    cambios: PropiedadAdminActualizar,
    service: ServiceDep,
    autenticacion: AdminCsrfDep,
    auditoria: AuditoriaDep,
) -> PropiedadAdminRespuesta:
    propiedad = service.actualizar_admin(propiedad_id, cambios)
    _sesion, usuario = autenticacion
    auditoria.registrar(
        usuario=usuario,
        accion="propiedad.actualizada_admin",
        recurso="propiedad",
        recurso_id=propiedad.id,
        detalles=cambios.model_dump(exclude_unset=True, mode="json"),
    )
    return PropiedadAdminRespuesta.model_validate(propiedad)
