import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.core.database import engine


def test_database_connection() -> None:
    """Comprueba que la aplicación puede conectarse a PostgreSQL."""

    with engine.connect() as connection:
        resultado = connection.execute(text("SELECT 1")).scalar_one()

    assert resultado == 1


def test_propiedades_table_exists() -> None:
    """Comprueba que el esquema inmobiliario esperado existe."""

    inspector = inspect(engine)
    tablas = inspector.get_table_names()

    assert "propiedades" in tablas
    assert "properties" not in tablas


def test_propiedades_columns() -> None:
    """Comprueba las columnas principales de la tabla propiedades."""

    inspector = inspect(engine)

    columnas = {columna["name"] for columna in inspector.get_columns("propiedades")}

    columnas_esperadas = {
        "id",
        "codigo",
        "slug",
        "titulo",
        "descripcion",
        "tipo_operacion",
        "tipo_propiedad",
        "precio",
        "moneda",
        "localidad",
        "zona",
        "dormitorios",
        "banios",
        "superficie_cubierta",
        "superficie_total",
        "estado",
        "destacada",
        "creado_en",
        "actualizado_en",
        "direccion",
        "latitud",
        "longitud",
        "mostrar_ubicacion_exacta",
    }

    assert columnas == columnas_esperadas


def test_propiedades_location_constraints_exist() -> None:
    inspector = inspect(engine)

    constraints = inspector.get_check_constraints("propiedades")
    nombres = {constraint["name"] for constraint in constraints}

    constraints_ubicacion = {
        "ck_propiedades_coordenadas_completas",
        "ck_propiedades_latitud_valida",
        "ck_propiedades_longitud_valida",
    }

    assert constraints_ubicacion.issubset(nombres)


def test_database_is_at_alembic_head() -> None:
    """Comprueba que PostgreSQL está en la última revisión de Alembic."""

    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    revision_head = script.get_current_head()

    with engine.connect() as connection:
        revision_database = connection.execute(
            text("SELECT version_num FROM alembic_version")
        ).scalar_one()

    assert revision_database == revision_head


def test_propiedades_ubicacion_exacta_es_false_por_defecto() -> None:
    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            mostrar_ubicacion_exacta = connection.execute(
                text("""
                    INSERT INTO propiedades (
                        codigo,
                        slug,
                        titulo,
                        descripcion,
                        tipo_operacion,
                        tipo_propiedad,
                        localidad,
                        latitud,
                        longitud
                    )
                    VALUES (
                        :codigo,
                        :slug,
                        :titulo,
                        :descripcion,
                        :tipo_operacion,
                        :tipo_propiedad,
                        :localidad,
                        :latitud,
                        :longitud
                    )
                    RETURNING mostrar_ubicacion_exacta
                    """),
                {
                    "codigo": "TEST-GEO-VALIDA",
                    "slug": "test-geo-valida",
                    "titulo": "Propiedad de prueba",
                    "descripcion": "Registro temporal para test de integración",
                    "tipo_operacion": "venta",
                    "tipo_propiedad": "casa",
                    "localidad": "Posadas",
                    "latitud": -27.3621,
                    "longitud": -55.9009,
                },
            ).scalar_one()

            assert mostrar_ubicacion_exacta is False
        finally:
            transaction.rollback()


@pytest.mark.parametrize(
    ("codigo", "slug", "latitud", "longitud"),
    [
        ("TEST-GEO-LAT", "test-geo-lat", 91.0, -55.9009),
        ("TEST-GEO-LON", "test-geo-lon", -27.3621, 181.0),
        ("TEST-GEO-INCOMPLETA", "test-geo-incompleta", -27.3621, None),
    ],
)
def test_propiedades_rechaza_coordenadas_invalidas(
    codigo: str,
    slug: str,
    latitud: float | None,
    longitud: float | None,
) -> None:
    with engine.connect() as connection:
        transaction = connection.begin()

        try:
            with pytest.raises(IntegrityError):
                connection.execute(
                    text("""
                        INSERT INTO propiedades (
                            codigo,
                            slug,
                            titulo,
                            descripcion,
                            tipo_operacion,
                            tipo_propiedad,
                            localidad,
                            latitud,
                            longitud
                        )
                        VALUES (
                            :codigo,
                            :slug,
                            :titulo,
                            :descripcion,
                            :tipo_operacion,
                            :tipo_propiedad,
                            :localidad,
                            :latitud,
                            :longitud
                        )
                        """),
                    {
                        "codigo": codigo,
                        "slug": slug,
                        "titulo": "Propiedad inválida de prueba",
                        "descripcion": "Registro temporal para validar constraints",
                        "tipo_operacion": "venta",
                        "tipo_propiedad": "casa",
                        "localidad": "Posadas",
                        "latitud": latitud,
                        "longitud": longitud,
                    },
                )
        finally:
            transaction.rollback()
