from typing import Any, Protocol

import boto3  # type: ignore[import-untyped]

from app.modules.imagenes.exceptions import AlmacenamientoImagenError


class AlmacenamientoImagenes(Protocol):
    def guardar(self, clave: str, contenido: bytes, *, content_type: str) -> None: ...

    def eliminar(self, clave: str) -> None: ...

    def obtener_url(self, clave: str, *, expiracion_segundos: int = 3600) -> str: ...


class AlmacenamientoS3:
    def __init__(
        self,
        *,
        bucket: str,
        endpoint_url: str | None,
        access_key_id: str | None,
        secret_access_key: str | None,
        region: str,
        use_ssl: bool,
        cliente: Any | None = None,
    ) -> None:
        self.bucket = bucket
        self.cliente = cliente or boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region,
            use_ssl=use_ssl,
        )

    def guardar(self, clave: str, contenido: bytes, *, content_type: str) -> None:
        try:
            self.cliente.put_object(
                Bucket=self.bucket,
                Key=clave,
                Body=contenido,
                ContentType=content_type,
                CacheControl="public, max-age=31536000, immutable",
            )
        except Exception as error:
            raise AlmacenamientoImagenError(
                "No fue posible guardar la imagen"
            ) from error

    def eliminar(self, clave: str) -> None:
        try:
            self.cliente.delete_object(Bucket=self.bucket, Key=clave)
        except Exception as error:
            raise AlmacenamientoImagenError(
                "No fue posible eliminar la imagen"
            ) from error

    def obtener_url(self, clave: str, *, expiracion_segundos: int = 3600) -> str:
        try:
            return str(
                self.cliente.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": self.bucket, "Key": clave},
                    ExpiresIn=expiracion_segundos,
                )
            )
        except Exception as error:
            raise AlmacenamientoImagenError(
                "No fue posible generar la URL de la imagen"
            ) from error
