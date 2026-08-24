from unittest.mock import Mock

import pytest

from app.modules.imagenes.exceptions import AlmacenamientoImagenError
from app.modules.imagenes.storage import AlmacenamientoS3


def crear_almacenamiento(
    cliente: Mock,
    *,
    public_base_url: str | None = None,
) -> AlmacenamientoS3:
    return AlmacenamientoS3(
        bucket="imagenes",
        endpoint_url="https://s3.example",
        access_key_id="access",
        secret_access_key="secret",
        region="auto",
        use_ssl=True,
        public_base_url=public_base_url,
        cliente=cliente,
    )


def test_guarda_objeto_con_cache_inmutable() -> None:
    cliente = Mock()
    almacenamiento = crear_almacenamiento(cliente)

    almacenamiento.guardar(
        "propiedades/7/imagen.webp",
        b"contenido",
        content_type="image/webp",
    )

    cliente.put_object.assert_called_once_with(
        Bucket="imagenes",
        Key="propiedades/7/imagen.webp",
        Body=b"contenido",
        ContentType="image/webp",
        CacheControl="public, max-age=31536000, immutable",
    )


def test_construye_url_publica_codificando_la_clave() -> None:
    cliente = Mock()
    almacenamiento = crear_almacenamiento(
        cliente,
        public_base_url="https://cdn.tophouse.com/",
    )

    url = almacenamiento.obtener_url("propiedades/7/frente jardín.webp")

    assert url == "https://cdn.tophouse.com/propiedades/7/frente%20jard%C3%ADn.webp"
    cliente.generate_presigned_url.assert_not_called()


def test_usa_url_firmada_sin_cdn_publico() -> None:
    cliente = Mock()
    cliente.generate_presigned_url.return_value = "https://s3.example/url-firmada"
    almacenamiento = crear_almacenamiento(cliente)

    url = almacenamiento.obtener_url(
        "propiedades/7/imagen.webp", expiracion_segundos=900
    )

    assert url == "https://s3.example/url-firmada"
    cliente.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": "imagenes", "Key": "propiedades/7/imagen.webp"},
        ExpiresIn=900,
    )


def test_traduce_error_del_cliente_al_guardar() -> None:
    cliente = Mock()
    cliente.put_object.side_effect = RuntimeError("fallo S3")
    almacenamiento = crear_almacenamiento(cliente)

    with pytest.raises(AlmacenamientoImagenError):
        almacenamiento.guardar(
            "propiedades/7/imagen.webp",
            b"contenido",
            content_type="image/webp",
        )
