from collections.abc import Iterator
from uuid import uuid4

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.modules.propiedades.exceptions import PropiedadDuplicadaError
from app.modules.propiedades.models import Propiedad
from app.modules.propiedades.repository import PropiedadRepository
from app.modules.propiedades.schemas import (
    PropiedadActualizar,
    PropiedadAdminActualizar,
    PropiedadCrear,
)


@pytest.fixture
def session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.execute(delete(Propiedad).where(Propiedad.codigo.like("TEST-REPO-%")))
        session.commit()
        session.close()


@pytest.fixture
def repository(session: Session) -> PropiedadRepository:
    return PropiedadRepository(session)


def datos_propiedad(*, sufijo: str | None = None) -> PropiedadCrear:
    identificador = sufijo or uuid4().hex[:10]
    return PropiedadCrear.model_validate(
        {
            "codigo": f"TEST-REPO-{identificador}",
            "titulo": "Casa de prueba",
            "descripcion": "Registro temporal del Repository",
            "tipo_operacion": "venta",
            "tipo_propiedad": "casa",
            "precio": "125000.00",
            "moneda": "USD",
            "localidad": "Merlo",
            "latitud": "-32.342900",
            "longitud": "-65.013900",
        }
    )


def crear_propiedad(
    repository: PropiedadRepository, *, sufijo: str | None = None
) -> Propiedad:
    identificador = sufijo or uuid4().hex[:10]
    return repository.crear(
        datos_propiedad(sufijo=identificador),
        slug=f"test-repo-{identificador}",
    )


def test_repository_crea_y_recupera_propiedad(
    repository: PropiedadRepository,
) -> None:
    propiedad = crear_propiedad(repository)

    recuperada_por_id = repository.obtener_por_id(propiedad.id)
    recuperada_por_slug = repository.obtener_por_slug(propiedad.slug)

    assert recuperada_por_id is not None
    assert recuperada_por_id.codigo == propiedad.codigo
    assert recuperada_por_slug is not None
    assert recuperada_por_slug.id == propiedad.id
    assert recuperada_por_slug.estado == "borrador"
    assert recuperada_por_slug.destacada is False


def test_repository_lista_con_total_y_paginacion(
    repository: PropiedadRepository,
) -> None:
    primera = crear_propiedad(repository)
    segunda = crear_propiedad(repository)

    propiedades, total = repository.listar(offset=0, limit=100)
    ids = {propiedad.id for propiedad in propiedades}

    assert total >= 2
    assert {primera.id, segunda.id}.issubset(ids)


@pytest.mark.parametrize(
    ("offset", "limit"),
    [(-1, 20), (0, 0), (0, 101)],
)
def test_repository_rechaza_paginacion_invalida(
    repository: PropiedadRepository,
    offset: int,
    limit: int,
) -> None:
    with pytest.raises(ValueError):
        repository.listar(offset=offset, limit=limit)


def test_repository_actualiza_patch_parcial(
    repository: PropiedadRepository,
) -> None:
    propiedad = crear_propiedad(repository)

    actualizada = repository.actualizar(
        propiedad,
        PropiedadActualizar.model_validate(
            {"titulo": "Título actualizado", "precio": "130000.00"}
        ),
    )

    assert actualizada.titulo == "Título actualizado"
    assert str(actualizada.precio) == "130000.00"
    assert actualizada.codigo == propiedad.codigo


def test_repository_actualiza_campos_administrativos(
    repository: PropiedadRepository,
) -> None:
    propiedad = crear_propiedad(repository)

    actualizada = repository.actualizar(
        propiedad,
        PropiedadAdminActualizar.model_validate(
            {"estado": "publicada", "destacada": True}
        ),
    )

    assert actualizada.estado == "publicada"
    assert actualizada.destacada is True


def test_repository_rechaza_codigo_duplicado(
    repository: PropiedadRepository,
) -> None:
    original = crear_propiedad(repository)
    duplicada = datos_propiedad()

    with pytest.raises(PropiedadDuplicadaError) as error:
        repository.crear(
            duplicada.model_copy(update={"codigo": original.codigo}),
            slug=f"test-repo-{uuid4().hex[:10]}",
        )

    assert error.value.campo == "codigo"


def test_repository_rechaza_slug_duplicado(
    repository: PropiedadRepository,
) -> None:
    original = crear_propiedad(repository)

    with pytest.raises(PropiedadDuplicadaError) as error:
        repository.crear(datos_propiedad(), slug=original.slug)

    assert error.value.campo == "slug"
