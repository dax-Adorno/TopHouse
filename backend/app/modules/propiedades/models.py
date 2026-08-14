from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Propiedad(Base):
    """Propiedad inmobiliaria administrada por TopHouse."""

    __tablename__ = "propiedades"

    __table_args__ = (
        CheckConstraint(
            "tipo_operacion IN ('venta', 'alquiler', 'temporario')",
            name="ck_propiedades_tipo_operacion",
        ),
        CheckConstraint(
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
            name="ck_propiedades_estado",
        ),
        CheckConstraint(
            "precio IS NULL OR precio >= 0",
            name="ck_propiedades_precio_no_negativo",
        ),
        CheckConstraint(
            "dormitorios IS NULL OR dormitorios >= 0",
            name="ck_propiedades_dormitorios_no_negativo",
        ),
        CheckConstraint(
            "banios IS NULL OR banios >= 0",
            name="ck_propiedades_banios_no_negativo",
        ),
        CheckConstraint(
            "superficie_cubierta IS NULL OR superficie_cubierta >= 0",
            name="ck_propiedades_superficie_cubierta_no_negativa",
        ),
        CheckConstraint(
            "superficie_total IS NULL OR superficie_total >= 0",
            name="ck_propiedades_superficie_total_no_negativa",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    codigo: Mapped[str] = mapped_column(
        String(32),
        unique=True,
        index=True,
    )

    slug: Mapped[str] = mapped_column(
        String(180),
        unique=True,
        index=True,
    )

    titulo: Mapped[str] = mapped_column(
        String(160),
    )

    descripcion: Mapped[str] = mapped_column(
        Text,
    )

    tipo_operacion: Mapped[str] = mapped_column(
        String(20),
        index=True,
    )

    tipo_propiedad: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )

    precio: Mapped[Decimal | None] = mapped_column(
        Numeric(14, 2),
        nullable=True,
        index=True,
    )

    moneda: Mapped[str | None] = mapped_column(
        String(3),
        nullable=True,
    )

    localidad: Mapped[str] = mapped_column(
        String(100),
        index=True,
    )

    zona: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )

    dormitorios: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    banios: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    superficie_cubierta: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    superficie_total: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    estado: Mapped[str] = mapped_column(
        String(20),
        default="borrador",
        server_default="borrador",
        index=True,
    )

    destacada: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="false",
        index=True,
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
