from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.dev_seed import DEMO_PROPERTIES, DEMO_PROPERTY_CODES, seed_demo_properties
from app.modules.propiedades.models import Propiedad


def _delete_demo_properties() -> None:
    with SessionLocal() as session:
        session.execute(
            delete(Propiedad).where(Propiedad.codigo.in_(DEMO_PROPERTY_CODES))
        )
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
