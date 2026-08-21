from typing import Annotated

from fastapi import Depends

from app.core.dependencies import SessionDep
from app.modules.propiedades.repository import PropiedadRepository
from app.modules.propiedades.service import PropiedadService


def obtener_repository(session: SessionDep) -> PropiedadRepository:
    return PropiedadRepository(session)


RepositoryDep = Annotated[PropiedadRepository, Depends(obtener_repository)]


def obtener_service(repository: RepositoryDep) -> PropiedadService:
    return PropiedadService(repository)


ServiceDep = Annotated[PropiedadService, Depends(obtener_service)]
