from typing import Literal, TypedDict

import boto3  # type: ignore[import-untyped]
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine

EstadoDependencia = Literal["ok", "unavailable"]


class EstadoReadiness(TypedDict):
    database: EstadoDependencia
    storage: EstadoDependencia


def comprobar_base_datos() -> None:
    """Comprueba que PostgreSQL acepta consultas."""
    with engine.connect() as conexion:
        conexion.execute(text("SELECT 1"))


def comprobar_almacenamiento() -> None:
    """Comprueba que el bucket configurado es accesible."""
    cliente = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
        use_ssl=settings.s3_use_ssl,
    )
    cliente.head_bucket(Bucket=settings.s3_bucket_name)


def comprobar_dependencias() -> EstadoReadiness:
    """Devuelve un estado no sensible de las dependencias críticas."""
    estado: EstadoReadiness = {
        "database": "ok",
        "storage": "ok",
    }
    try:
        comprobar_base_datos()
    except Exception:
        estado["database"] = "unavailable"
    try:
        comprobar_almacenamiento()
    except Exception:
        estado["storage"] = "unavailable"
    return estado
