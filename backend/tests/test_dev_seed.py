from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.dev_seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_PROPERTIES,
    DEMO_PROPERTY_CODES,
    LEGACY_DEMO_ADMIN_EMAILS,
    seed_demo_admin,
    seed_demo_properties,
)
from app.modules.propiedades.models import Propiedad
from app.modules.usuarios.models import RegistroAuditoria, SesionUsuario, Usuario


def _delete_demo_properties() -> None:
    with SessionLocal() as session:
        session.execute(
            delete(Propiedad).where(Propiedad.codigo.in_(DEMO_PROPERTY_CODES))
        )
        session.commit()


def _delete_demo_admin() -> None:
    with SessionLocal() as session:
        usuarios = list(
            session.scalars(
                select(Usuario).where(
                    Usuario.email.in_((DEMO_ADMIN_EMAIL, *LEGACY_DEMO_ADMIN_EMAILS))
                )
            )
        )
        for usuario in usuarios:
            session.execute(
                delete(RegistroAuditoria).where(
                    RegistroAuditoria.usuario_id == usuario.id
                )
            )
            session.execute(
                delete(SesionUsuario).where(SesionUsuario.usuario_id == usuario.id)
            )
            session.delete(usuario)
        session.commit()


def test_seed_demo_properties_is_idempotent() -> None:
    _delete_demo_properties()

    try:
        with SessionLocal() as session:
            first_result = seed_demo_properties(session)
            session.commit()

        with SessionLocal() as session:
            second_result = seed_demo_properties(session)
            session.commit()

            propiedades = list(
                session.scalars(
                    select(Propiedad).where(Propiedad.codigo.in_(DEMO_PROPERTY_CODES))
                )
            )

        assert first_result.created == len(DEMO_PROPERTIES)
        assert first_result.updated == 0
        assert second_result.created == 0
        assert second_result.updated == len(DEMO_PROPERTIES)
        assert len(propiedades) == len(DEMO_PROPERTIES)
        assert {propiedad.estado for propiedad in propiedades} == {"publicada"}
        assert any(propiedad.destacada for propiedad in propiedades)
    finally:
        _delete_demo_properties()


def test_seed_demo_admin_is_idempotent() -> None:
    _delete_demo_admin()

    try:
        with SessionLocal() as session:
            first_result = seed_demo_admin(session)
            session.commit()

        with SessionLocal() as session:
            second_result = seed_demo_admin(session)
            session.commit()

            usuario = session.scalar(
                select(Usuario).where(Usuario.email == DEMO_ADMIN_EMAIL)
            )

        assert first_result.created == 1
        assert first_result.updated == 0
        assert second_result.created == 0
        assert second_result.updated == 1
        assert usuario is not None
        assert usuario.rol == "administrador"
        assert usuario.activo is True
    finally:
        _delete_demo_admin()
