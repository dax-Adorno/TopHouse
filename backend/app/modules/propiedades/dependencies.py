from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.propiedades.repository import PropiedadRepository
from app.modules.propiedades.service import PropiedadService


def obtener_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


SessionDep = Annotated[Session, Depends(obtener_session)]


def obtener_repository(session: SessionDep) -> PropiedadRepository:
    return PropiedadRepository(session)


RepositoryDep = Annotated[PropiedadRepository, Depends(obtener_repository)]


def obtener_service(repository: RepositoryDep) -> PropiedadService:
    return PropiedadService(repository)


ServiceDep = Annotated[PropiedadService, Depends(obtener_service)]
