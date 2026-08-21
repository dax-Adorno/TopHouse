"""add property images

Revision ID: e51a829cd037
Revises: d34c8a1f0b72
Create Date: 2026-08-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "e51a829cd037"
down_revision: str | Sequence[str] | None = "d34c8a1f0b72"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "imagenes_propiedad",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("propiedad_id", sa.Integer(), nullable=False),
        sa.Column("clave_objeto", sa.String(length=512), nullable=False),
        sa.Column("clave_thumbnail", sa.String(length=512), nullable=False),
        sa.Column("nombre_original", sa.String(length=255), nullable=False),
        sa.Column("mime_type", sa.String(length=32), nullable=False),
        sa.Column("tamanio_bytes", sa.Integer(), nullable=False),
        sa.Column("ancho", sa.Integer(), nullable=False),
        sa.Column("alto", sa.Integer(), nullable=False),
        sa.Column("orden", sa.Integer(), nullable=False),
        sa.Column(
            "es_portada",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "ancho BETWEEN 320 AND 12000 AND alto BETWEEN 320 AND 12000",
            name="ck_imagenes_propiedad_dimensiones",
        ),
        sa.CheckConstraint(
            "mime_type IN ('image/jpeg', 'image/png', 'image/webp')",
            name="ck_imagenes_propiedad_mime_type",
        ),
        sa.CheckConstraint("orden >= 0", name="ck_imagenes_propiedad_orden"),
        sa.CheckConstraint(
            "tamanio_bytes > 0 AND tamanio_bytes <= 10485760",
            name="ck_imagenes_propiedad_tamanio",
        ),
        sa.ForeignKeyConstraint(
            ["propiedad_id"], ["propiedades.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("clave_objeto"),
        sa.UniqueConstraint("clave_thumbnail"),
        sa.UniqueConstraint(
            "propiedad_id",
            "orden",
            name="uq_imagenes_propiedad_propiedad_orden",
        ),
    )
    op.create_index(
        op.f("ix_imagenes_propiedad_propiedad_id"),
        "imagenes_propiedad",
        ["propiedad_id"],
        unique=False,
    )
    op.create_index(
        "uq_imagenes_propiedad_portada",
        "imagenes_propiedad",
        ["propiedad_id"],
        unique=True,
        postgresql_where=sa.text("es_portada"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_imagenes_propiedad_portada",
        table_name="imagenes_propiedad",
        postgresql_where=sa.text("es_portada"),
    )
    op.drop_index(
        op.f("ix_imagenes_propiedad_propiedad_id"),
        table_name="imagenes_propiedad",
    )
    op.drop_table("imagenes_propiedad")
