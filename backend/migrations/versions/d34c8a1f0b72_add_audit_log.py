"""add audit log

Revision ID: d34c8a1f0b72
Revises: b9f41a27c6d2
Create Date: 2026-08-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d34c8a1f0b72"
down_revision: str | Sequence[str] | None = "b9f41a27c6d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "registros_auditoria",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column("usuario_email", sa.String(length=254), nullable=False),
        sa.Column("accion", sa.String(length=60), nullable=False),
        sa.Column("recurso", sa.String(length=60), nullable=False),
        sa.Column("recurso_id", sa.String(length=80), nullable=False),
        sa.Column("detalles", sa.JSON(), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for columna in ("accion", "creado_en", "recurso", "recurso_id", "usuario_id"):
        op.create_index(
            op.f(f"ix_registros_auditoria_{columna}"),
            "registros_auditoria",
            [columna],
            unique=False,
        )


def downgrade() -> None:
    for columna in ("usuario_id", "recurso_id", "recurso", "creado_en", "accion"):
        op.drop_index(
            op.f(f"ix_registros_auditoria_{columna}"),
            table_name="registros_auditoria",
        )
    op.drop_table("registros_auditoria")
