from typing import Annotated

from fastapi import Depends

from app.core.config import settings
from app.core.dependencies import SessionDep
from app.modules.imagenes.repository import ImagenRepository
from app.modules.imagenes.service import ImagenService
from app.modules.imagenes.storage import AlmacenamientoS3
from app.modules.propiedades.repository import PropiedadRepository
from app.modules.propiedades.service import PropiedadService


def obtener_imagen_service(session: SessionDep) -> ImagenService:
    almacenamiento = AlmacenamientoS3(
        bucket=settings.s3_bucket_name,
        endpoint_url=settings.s3_endpoint_url,
        access_key_id=settings.s3_access_key_id,
        secret_access_key=settings.s3_secret_access_key,
        region=settings.s3_region,
        use_ssl=settings.s3_use_ssl,
        public_base_url=settings.s3_public_base_url,
    )
    return ImagenService(
        ImagenRepository(session),
        PropiedadService(PropiedadRepository(session)),
        almacenamiento,
    )


ImagenServiceDep = Annotated[ImagenService, Depends(obtener_imagen_service)]
