"""translate property domain to spanish

Revision ID: c7b62cd89c9e
Revises: 494b15d982da
Create Date: 2026-08-14 11:31:14.005409

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c7b62cd89c9e"
down_revision: str | Sequence[str] | None = "494b15d982da"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Traduce el dominio de propiedades al castellano sin perder datos."""

    # 1. Renombrar tabla

    op.rename_table("properties", "propiedades")

    # 2. Renombrar columnas

    op.alter_column(
        "propiedades",
        "code",
        new_column_name="codigo",
    )
    op.alter_column(
        "propiedades",
        "title",
        new_column_name="titulo",
    )
    op.alter_column(
        "propiedades",
        "description",
        new_column_name="descripcion",
    )
    op.alter_column(
        "propiedades",
        "operation_type",
        new_column_name="tipo_operacion",
    )
    op.alter_column(
        "propiedades",
        "property_type",
        new_column_name="tipo_propiedad",
    )
    op.alter_column(
        "propiedades",
        "price",
        new_column_name="precio",
    )
    op.alter_column(
        "propiedades",
        "currency",
        new_column_name="moneda",
    )
    op.alter_column(
        "propiedades",
        "city",
        new_column_name="localidad",
    )
    op.alter_column(
        "propiedades",
        "zone",
        new_column_name="zona",
    )
    op.alter_column(
        "propiedades",
        "bedrooms",
        new_column_name="dormitorios",
    )
    op.alter_column(
        "propiedades",
        "bathrooms",
        new_column_name="banios",
    )
    op.alter_column(
        "propiedades",
        "covered_area",
        new_column_name="superficie_cubierta",
    )
    op.alter_column(
        "propiedades",
        "total_area",
        new_column_name="superficie_total",
    )
    op.alter_column(
        "propiedades",
        "status",
        new_column_name="estado",
    )
    op.alter_column(
        "propiedades",
        "featured",
        new_column_name="destacada",
    )
    op.alter_column(
        "propiedades",
        "created_at",
        new_column_name="creado_en",
    )
    op.alter_column(
        "propiedades",
        "updated_at",
        new_column_name="actualizado_en",
    )

    # 3. Eliminar temporalmente los checks cuyos valores cambian

    op.drop_constraint(
        "ck_properties_operation_type",
        "propiedades",
        type_="check",
    )
    op.drop_constraint(
        "ck_properties_status",
        "propiedades",
        type_="check",
    )

    # 4. Traducir datos existentes

    op.execute(
        sa.text(
            """
            UPDATE propiedades
            SET tipo_operacion = CASE tipo_operacion
                WHEN 'sale' THEN 'venta'
                WHEN 'rent' THEN 'alquiler'
                WHEN 'temporary' THEN 'temporario'
                ELSE tipo_operacion
            END
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE propiedades
            SET estado = CASE estado
                WHEN 'draft' THEN 'borrador'
                WHEN 'published' THEN 'publicada'
                WHEN 'paused' THEN 'pausada'
                WHEN 'reserved' THEN 'reservada'
                WHEN 'rented' THEN 'alquilada'
                WHEN 'sold' THEN 'vendida'
                WHEN 'unavailable' THEN 'no_disponible'
                ELSE estado
            END
            """
        )
    )

    # 5. Cambiar el valor por defecto de estado

    op.alter_column(
        "propiedades",
        "estado",
        existing_type=sa.String(length=20),
        server_default=sa.text("'borrador'"),
    )

    # 6. Crear los nuevos checks en castellano

    op.create_check_constraint(
        "ck_propiedades_tipo_operacion",
        "propiedades",
        "tipo_operacion IN ('venta', 'alquiler', 'temporario')",
    )

    op.create_check_constraint(
        "ck_propiedades_estado",
        "propiedades",
        """
        estado IN (
            'borrador',
            'publicada',
            'pausada',
            'reservada',
            'alquilada',
            'vendida',
            'no_disponible'
        )
        """,
    )

    # 7. Renombrar constraints numéricos

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_properties_bathrooms_non_negative
            TO ck_propiedades_banios_no_negativo
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_properties_bedrooms_non_negative
            TO ck_propiedades_dormitorios_no_negativo
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_properties_covered_area_non_negative
            TO ck_propiedades_superficie_cubierta_no_negativa
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_properties_price_non_negative
            TO ck_propiedades_precio_no_negativo
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_properties_total_area_non_negative
            TO ck_propiedades_superficie_total_no_negativa
            """
        )
    )

    # 8. Renombrar primary key

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT properties_pkey
            TO propiedades_pkey
            """
        )
    )

    # 9. Renombrar índices

    op.execute(
        sa.text("ALTER INDEX ix_properties_city RENAME TO ix_propiedades_localidad")
    )
    op.execute(
        sa.text("ALTER INDEX ix_properties_code RENAME TO ix_propiedades_codigo")
    )
    op.execute(
        sa.text("ALTER INDEX ix_properties_featured RENAME TO ix_propiedades_destacada")
    )
    op.execute(
        sa.text(
            """
            ALTER INDEX ix_properties_operation_type
            RENAME TO ix_propiedades_tipo_operacion
            """
        )
    )
    op.execute(
        sa.text("ALTER INDEX ix_properties_price RENAME TO ix_propiedades_precio")
    )
    op.execute(
        sa.text(
            """
            ALTER INDEX ix_properties_property_type
            RENAME TO ix_propiedades_tipo_propiedad
            """
        )
    )
    op.execute(sa.text("ALTER INDEX ix_properties_slug RENAME TO ix_propiedades_slug"))
    op.execute(
        sa.text("ALTER INDEX ix_properties_status RENAME TO ix_propiedades_estado")
    )
    op.execute(sa.text("ALTER INDEX ix_properties_zone RENAME TO ix_propiedades_zona"))

    # 10. Renombrar la secuencia del id

    op.execute(
        sa.text(
            """
            ALTER SEQUENCE properties_id_seq
            RENAME TO propiedades_id_seq
            """
        )
    )


def downgrade() -> None:
    """Restaura el dominio original en inglés."""

    # 1. Eliminar checks castellanos cuyos valores cambiarán

    op.drop_constraint(
        "ck_propiedades_tipo_operacion",
        "propiedades",
        type_="check",
    )
    op.drop_constraint(
        "ck_propiedades_estado",
        "propiedades",
        type_="check",
    )

    # 2. Restaurar datos originales

    op.execute(
        sa.text(
            """
            UPDATE propiedades
            SET tipo_operacion = CASE tipo_operacion
                WHEN 'venta' THEN 'sale'
                WHEN 'alquiler' THEN 'rent'
                WHEN 'temporario' THEN 'temporary'
                ELSE tipo_operacion
            END
            """
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE propiedades
            SET estado = CASE estado
                WHEN 'borrador' THEN 'draft'
                WHEN 'publicada' THEN 'published'
                WHEN 'pausada' THEN 'paused'
                WHEN 'reservada' THEN 'reserved'
                WHEN 'alquilada' THEN 'rented'
                WHEN 'vendida' THEN 'sold'
                WHEN 'no_disponible' THEN 'unavailable'
                ELSE estado
            END
            """
        )
    )

    # 3. Restaurar default original

    op.alter_column(
        "propiedades",
        "estado",
        existing_type=sa.String(length=20),
        server_default=sa.text("'draft'"),
    )

    # 4. Restaurar nombres de constraints

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_propiedades_banios_no_negativo
            TO ck_properties_bathrooms_non_negative
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_propiedades_dormitorios_no_negativo
            TO ck_properties_bedrooms_non_negative
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_propiedades_superficie_cubierta_no_negativa
            TO ck_properties_covered_area_non_negative
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_propiedades_precio_no_negativo
            TO ck_properties_price_non_negative
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT ck_propiedades_superficie_total_no_negativa
            TO ck_properties_total_area_non_negative
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE propiedades
            RENAME CONSTRAINT propiedades_pkey
            TO properties_pkey
            """
        )
    )

    # 5. Restaurar índices

    op.execute(
        sa.text("ALTER INDEX ix_propiedades_localidad RENAME TO ix_properties_city")
    )
    op.execute(
        sa.text("ALTER INDEX ix_propiedades_codigo RENAME TO ix_properties_code")
    )
    op.execute(
        sa.text("ALTER INDEX ix_propiedades_destacada RENAME TO ix_properties_featured")
    )
    op.execute(
        sa.text(
            """
            ALTER INDEX ix_propiedades_tipo_operacion
            RENAME TO ix_properties_operation_type
            """
        )
    )
    op.execute(
        sa.text("ALTER INDEX ix_propiedades_precio RENAME TO ix_properties_price")
    )
    op.execute(
        sa.text(
            """
            ALTER INDEX ix_propiedades_tipo_propiedad
            RENAME TO ix_properties_property_type
            """
        )
    )
    op.execute(sa.text("ALTER INDEX ix_propiedades_slug RENAME TO ix_properties_slug"))
    op.execute(
        sa.text("ALTER INDEX ix_propiedades_estado RENAME TO ix_properties_status")
    )
    op.execute(sa.text("ALTER INDEX ix_propiedades_zona RENAME TO ix_properties_zone"))

    # 6. Restaurar nombre de secuencia

    op.execute(
        sa.text(
            """
            ALTER SEQUENCE propiedades_id_seq
            RENAME TO properties_id_seq
            """
        )
    )

    # 7. Restaurar nombres de columnas

    op.alter_column(
        "propiedades",
        "codigo",
        new_column_name="code",
    )
    op.alter_column(
        "propiedades",
        "titulo",
        new_column_name="title",
    )
    op.alter_column(
        "propiedades",
        "descripcion",
        new_column_name="description",
    )
    op.alter_column(
        "propiedades",
        "tipo_operacion",
        new_column_name="operation_type",
    )
    op.alter_column(
        "propiedades",
        "tipo_propiedad",
        new_column_name="property_type",
    )
    op.alter_column(
        "propiedades",
        "precio",
        new_column_name="price",
    )
    op.alter_column(
        "propiedades",
        "moneda",
        new_column_name="currency",
    )
    op.alter_column(
        "propiedades",
        "localidad",
        new_column_name="city",
    )
    op.alter_column(
        "propiedades",
        "zona",
        new_column_name="zone",
    )
    op.alter_column(
        "propiedades",
        "dormitorios",
        new_column_name="bedrooms",
    )
    op.alter_column(
        "propiedades",
        "banios",
        new_column_name="bathrooms",
    )
    op.alter_column(
        "propiedades",
        "superficie_cubierta",
        new_column_name="covered_area",
    )
    op.alter_column(
        "propiedades",
        "superficie_total",
        new_column_name="total_area",
    )
    op.alter_column(
        "propiedades",
        "estado",
        new_column_name="status",
    )
    op.alter_column(
        "propiedades",
        "destacada",
        new_column_name="featured",
    )
    op.alter_column(
        "propiedades",
        "creado_en",
        new_column_name="created_at",
    )
    op.alter_column(
        "propiedades",
        "actualizado_en",
        new_column_name="updated_at",
    )

    # 8. Restaurar tabla original

    op.rename_table("propiedades", "properties")

    # 9. Restaurar checks originales

    op.create_check_constraint(
        "ck_properties_operation_type",
        "properties",
        "operation_type IN ('sale', 'rent', 'temporary')",
    )

    op.create_check_constraint(
        "ck_properties_status",
        "properties",
        """
        status IN (
            'draft',
            'published',
            'paused',
            'reserved',
            'rented',
            'sold',
            'unavailable'
        )
        """,
    )
