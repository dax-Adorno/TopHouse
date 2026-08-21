from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.modules.imagenes.constants import MAX_TAMANIO_IMAGEN_BYTES
from app.modules.imagenes.dependencies import ImagenServiceDep
from app.modules.imagenes.schemas import ImagenApiRespuesta, ImagenOrdenActualizar
from app.modules.usuarios.audit import AuditoriaDep
from app.modules.usuarios.dependencies import (
    CsrfDep,
    obtener_autenticacion,
)

router = APIRouter(
    prefix="/api/v1/propiedades/{propiedad_id}/imagenes",
    tags=["Imágenes"],
    dependencies=[Depends(obtener_autenticacion)],
)


@router.get("", response_model=list[ImagenApiRespuesta])
def listar_imagenes(
    propiedad_id: int,
    service: ImagenServiceDep,
) -> list[ImagenApiRespuesta]:
    return [service.respuesta(imagen) for imagen in service.listar(propiedad_id)]


@router.post(
    "",
    response_model=ImagenApiRespuesta,
    status_code=status.HTTP_201_CREATED,
)
async def cargar_imagen(
    propiedad_id: int,
    service: ImagenServiceDep,
    autenticacion: CsrfDep,
    auditoria: AuditoriaDep,
    archivo: Annotated[UploadFile, File()],
) -> ImagenApiRespuesta:
    contenido = await archivo.read(MAX_TAMANIO_IMAGEN_BYTES + 1)
    imagen = service.agregar(
        propiedad_id=propiedad_id,
        nombre_original=archivo.filename or "imagen",
        contenido=contenido,
        mime_type_declarado=archivo.content_type,
    )
    _sesion, usuario = autenticacion
    auditoria.registrar(
        usuario=usuario,
        accion="imagen.creada",
        recurso="imagen_propiedad",
        recurso_id=imagen.id,
        detalles={"propiedad_id": propiedad_id},
    )
    return service.respuesta(imagen)


@router.put("/orden", response_model=list[ImagenApiRespuesta])
def reordenar_imagenes(
    propiedad_id: int,
    datos: ImagenOrdenActualizar,
    service: ImagenServiceDep,
    autenticacion: CsrfDep,
    auditoria: AuditoriaDep,
) -> list[ImagenApiRespuesta]:
    imagenes = service.reordenar(propiedad_id, datos.imagen_ids)
    _sesion, usuario = autenticacion
    auditoria.registrar(
        usuario=usuario,
        accion="imagenes.reordenadas",
        recurso="propiedad",
        recurso_id=propiedad_id,
        detalles={"imagen_ids": datos.imagen_ids},
    )
    return [service.respuesta(imagen) for imagen in imagenes]


@router.put("/{imagen_id}/portada", response_model=ImagenApiRespuesta)
def establecer_portada(
    propiedad_id: int,
    imagen_id: int,
    service: ImagenServiceDep,
    autenticacion: CsrfDep,
    auditoria: AuditoriaDep,
) -> ImagenApiRespuesta:
    imagen = service.establecer_portada(propiedad_id, imagen_id)
    _sesion, usuario = autenticacion
    auditoria.registrar(
        usuario=usuario,
        accion="imagen.portada_establecida",
        recurso="imagen_propiedad",
        recurso_id=imagen.id,
        detalles={"propiedad_id": propiedad_id},
    )
    return service.respuesta(imagen)


@router.delete("/{imagen_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_imagen(
    propiedad_id: int,
    imagen_id: int,
    service: ImagenServiceDep,
    autenticacion: CsrfDep,
    auditoria: AuditoriaDep,
) -> None:
    service.eliminar(propiedad_id, imagen_id)
    _sesion, usuario = autenticacion
    auditoria.registrar(
        usuario=usuario,
        accion="imagen.eliminada",
        recurso="imagen_propiedad",
        recurso_id=imagen_id,
        detalles={"propiedad_id": propiedad_id},
    )
