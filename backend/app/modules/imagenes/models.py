from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    UniqueConstraint,
    false,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ImagenPropiedad(Base):
    """Metadatos de una imagen procesada y almacenada fuera de PostgreSQL."""

    __tablename__ = "imagenes_propiedad"
    __table_args__ = (
        CheckConstraint("orden >= 0", name="ck_imagenes_propiedad_orden"),
        CheckConstraint(
            "tamanio_bytes > 0 AND tamanio_bytes <= 10485760",
            name="ck_imagenes_propiedad_tamanio",
        ),
        CheckConstraint(
            "ancho BETWEEN 320 AND 12000 AND alto BETWEEN 320 AND 12000",
            name="ck_imagenes_propiedad_dimensiones",
        ),
        CheckConstraint(
            "mime_type IN ('image/jpeg', 'image/png', 'image/webp')",
            name="ck_imagenes_propiedad_mime_type",
        ),
        UniqueConstraint(
            "propiedad_id",
            "orden",
            name="uq_imagenes_propiedad_propiedad_orden",
        ),
        Index(
            "uq_imagenes_propiedad_portada",
            "propiedad_id",
            unique=True,
            postgresql_where=text("es_portada"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    propiedad_id: Mapped[int] = mapped_column(
        ForeignKey("propiedades.id", ondelete="CASCADE"),
        index=True,
    )
    clave_objeto: Mapped[str] = mapped_column(String(512), unique=True)
    clave_thumbnail: Mapped[str] = mapped_column(String(512), unique=True)
    nombre_original: Mapped[str] = mapped_column(String(255))
    mime_type: Mapped[str] = mapped_column(String(32))
    tamanio_bytes: Mapped[int] = mapped_column()
    ancho: Mapped[int] = mapped_column()
    alto: Mapped[int] = mapped_column()
    orden: Mapped[int] = mapped_column(default=0)
    es_portada: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default=false(),
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
