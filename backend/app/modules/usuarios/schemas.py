from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.usuarios.constants import RolUsuario


class UsuarioCrear(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    email: EmailStr
    nombre: str = Field(min_length=1, max_length=120)
    contrasena: str = Field(min_length=12, max_length=128)
    rol: RolUsuario = RolUsuario.OPERADOR


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )

    id: int
    email: EmailStr
    nombre: str
    rol: RolUsuario
    activo: bool
    ultimo_acceso_en: datetime | None
    creado_en: datetime
    actualizado_en: datetime
