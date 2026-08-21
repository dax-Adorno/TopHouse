from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.modules.imagenes.schemas import ImagenPublicaRespuesta


class TipoOperacion(StrEnum):
    VENTA = "venta"
    ALQUILER = "alquiler"
    TEMPORARIO = "temporario"


class EstadoPropiedad(StrEnum):
    BORRADOR = "borrador"
    PUBLICADA = "publicada"
    PAUSADA = "pausada"
    RESERVADA = "reservada"
    ALQUILADA = "alquilada"
    VENDIDA = "vendida"
    NO_DISPONIBLE = "no_disponible"


class SchemaBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class PropiedadContenidoBase(SchemaBase):
    codigo: str = Field(min_length=1, max_length=32)
    titulo: str = Field(min_length=1, max_length=160)
    descripcion: str = Field(min_length=1)

    tipo_operacion: TipoOperacion
    tipo_propiedad: str = Field(min_length=1, max_length=50)

    precio: Decimal | None = Field(default=None, ge=0)
    moneda: str | None = Field(default=None, min_length=3, max_length=3)

    localidad: str = Field(min_length=1, max_length=100)
    zona: str | None = Field(default=None, max_length=100)

    dormitorios: int | None = Field(default=None, ge=0)
    banios: int | None = Field(default=None, ge=0)

    superficie_cubierta: Decimal | None = Field(default=None, ge=0)
    superficie_total: Decimal | None = Field(default=None, ge=0)


class PropiedadBase(PropiedadContenidoBase):
    direccion: str | None = Field(default=None, max_length=200)
    latitud: Decimal | None = Field(default=None, ge=-90, le=90)
    longitud: Decimal | None = Field(default=None, ge=-180, le=180)
    mostrar_ubicacion_exacta: bool = False

    @model_validator(mode="after")
    def validar_coordenadas_completas(self) -> Self:
        if (self.latitud is None) != (self.longitud is None):
            raise ValueError("latitud y longitud deben enviarse juntas")
        return self


class PropiedadCrear(PropiedadBase):
    """Datos aceptados al crear una propiedad.

    Slug, estado, destacado, identificador y timestamps son controlados por el
    backend y no forman parte de este contrato.
    """


class PropiedadActualizar(SchemaBase):
    """Campos editables comunes para un PATCH de propiedad."""

    codigo: str | None = Field(default=None, min_length=1, max_length=32)
    titulo: str | None = Field(default=None, min_length=1, max_length=160)
    descripcion: str | None = Field(default=None, min_length=1)

    tipo_operacion: TipoOperacion | None = None
    tipo_propiedad: str | None = Field(default=None, min_length=1, max_length=50)

    precio: Decimal | None = Field(default=None, ge=0)
    moneda: str | None = Field(default=None, min_length=3, max_length=3)

    localidad: str | None = Field(default=None, min_length=1, max_length=100)
    zona: str | None = Field(default=None, max_length=100)

    direccion: str | None = Field(default=None, max_length=200)
    latitud: Decimal | None = Field(default=None, ge=-90, le=90)
    longitud: Decimal | None = Field(default=None, ge=-180, le=180)
    mostrar_ubicacion_exacta: bool | None = None

    dormitorios: int | None = Field(default=None, ge=0)
    banios: int | None = Field(default=None, ge=0)

    superficie_cubierta: Decimal | None = Field(default=None, ge=0)
    superficie_total: Decimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validar_patch_de_coordenadas(self) -> Self:
        latitud_enviada = "latitud" in self.model_fields_set
        longitud_enviada = "longitud" in self.model_fields_set
        if latitud_enviada != longitud_enviada:
            raise ValueError("latitud y longitud deben actualizarse juntas")
        return self


class PropiedadAdminActualizar(PropiedadActualizar):
    """PATCH administrativo, incluidas decisiones operativas controladas."""

    estado: EstadoPropiedad | None = None
    destacada: bool | None = None


class PropiedadAdminRespuesta(PropiedadBase):
    """Respuesta administrativa con ubicación exacta y datos internos."""

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
        str_strip_whitespace=True,
    )

    id: int
    slug: str
    estado: EstadoPropiedad
    destacada: bool
    creado_en: datetime
    actualizado_en: datetime


class PropiedadPublicaRespuesta(PropiedadContenidoBase):
    """Respuesta pública que no puede serializar dirección ni coordenadas."""

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        str_strip_whitespace=True,
    )

    id: int
    slug: str
    estado: EstadoPropiedad
    destacada: bool
    creado_en: datetime
    actualizado_en: datetime
    imagenes: list[ImagenPublicaRespuesta] = Field(default_factory=list)


class PaginaPropiedadesAdmin(SchemaBase):
    items: list[PropiedadAdminRespuesta]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)


class PaginaPropiedadesPublicas(SchemaBase):
    items: list[PropiedadPublicaRespuesta]
    total: int = Field(ge=0)
    offset: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
