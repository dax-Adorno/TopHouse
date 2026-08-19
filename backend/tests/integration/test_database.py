from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import inspect, text

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
    }

    assert columnas == columnas_esperadas


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
