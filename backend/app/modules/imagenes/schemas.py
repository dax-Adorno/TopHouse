from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.imagenes.constants import (
    MAX_DIMENSION_IMAGEN,
    MAX_TAMANIO_IMAGEN_BYTES,
    MIME_TYPES_PERMITIDOS,
    MIN_DIMENSION_IMAGEN,
)


class ImagenMetadatosCrear(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    clave_objeto: str = Field(min_length=1, max_length=512)
    clave_thumbnail: str = Field(min_length=1, max_length=512)
    nombre_original: str = Field(min_length=1, max_length=255)
    mime_type: str
    tamanio_bytes: int = Field(gt=0, le=MAX_TAMANIO_IMAGEN_BYTES)
    ancho: int = Field(ge=MIN_DIMENSION_IMAGEN, le=MAX_DIMENSION_IMAGEN)
    alto: int = Field(ge=MIN_DIMENSION_IMAGEN, le=MAX_DIMENSION_IMAGEN)
    orden: int = Field(ge=0)
    es_portada: bool = False

    @field_validator("mime_type")
    @classmethod
    def validar_mime_type(cls, valor: str) -> str:
        normalizado = valor.lower()
        if normalizado not in MIME_TYPES_PERMITIDOS:
            raise ValueError("formato de imagen no permitido")
        return normalizado


class ImagenRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="ignore")

    id: int
    propiedad_id: int
    nombre_original: str
    mime_type: str
    tamanio_bytes: int
    ancho: int
    alto: int
    orden: int
    es_portada: bool
    creado_en: datetime


class ImagenApiRespuesta(ImagenRespuesta):
    url: str
    url_thumbnail: str


class ImagenOrdenActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    imagen_ids: list[int] = Field(min_length=1, max_length=20)

    @field_validator("imagen_ids")
    @classmethod
    def validar_ids_unicos(cls, valores: list[int]) -> list[int]:
        if any(valor <= 0 for valor in valores):
            raise ValueError("los ids deben ser positivos")
        if len(valores) != len(set(valores)):
            raise ValueError("los ids de imágenes no pueden repetirse")
        return valores
