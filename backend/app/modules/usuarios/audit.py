from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import SessionDep
from app.modules.usuarios.models import RegistroAuditoria, Usuario


class AuditoriaService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def registrar(
        self,
        *,
        usuario: Usuario,
        accion: str,
        recurso: str,
        recurso_id: int | str,
        detalles: dict[str, object] | None = None,
    ) -> RegistroAuditoria:
        registro = RegistroAuditoria(
            usuario_id=usuario.id,
            usuario_email=usuario.email,
            accion=accion,
            recurso=recurso,
            recurso_id=str(recurso_id),
            detalles=detalles or {},
        )
        self.session.add(registro)
        self.session.commit()
        self.session.refresh(registro)
        return registro


def obtener_auditoria(session: SessionDep) -> AuditoriaService:
    return AuditoriaService(session)


AuditoriaDep = Annotated[AuditoriaService, Depends(obtener_auditoria)]
