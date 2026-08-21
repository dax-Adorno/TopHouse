"""add user sessions

Revision ID: b9f41a27c6d2
Revises: e4386fa00510
Create Date: 2026-08-21
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b9f41a27c6d2"
down_revision: str | Sequence[str] | None = "e4386fa00510"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "sesiones_usuario",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("csrf_token_hash", sa.String(length=64), nullable=False),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revocada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "creada_en",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_sesiones_usuario_expira_en"),
        "sesiones_usuario",
        ["expira_en"],
        unique=False,
    )
    op.create_index(
        op.f("ix_sesiones_usuario_token_hash"),
        "sesiones_usuario",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        op.f("ix_sesiones_usuario_usuario_id"),
        "sesiones_usuario",
        ["usuario_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_sesiones_usuario_usuario_id"),
        table_name="sesiones_usuario",
    )
    op.drop_index(
        op.f("ix_sesiones_usuario_token_hash"),
        table_name="sesiones_usuario",
    )
    op.drop_index(
        op.f("ix_sesiones_usuario_expira_en"),
        table_name="sesiones_usuario",
    )
    op.drop_table("sesiones_usuario")
