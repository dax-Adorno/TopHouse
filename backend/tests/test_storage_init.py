import json
from unittest.mock import Mock, patch

from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from app.core.config import settings
from app.storage_init import preparar_bucket


@patch("app.storage_init.boto3.client")
def test_crea_bucket_con_lectura_publica_de_objetos(crear_cliente: Mock) -> None:
    cliente = crear_cliente.return_value

    preparar_bucket()

    cliente.create_bucket.assert_called_once_with(Bucket=settings.s3_bucket_name)
    llamada = cliente.put_bucket_policy.call_args.kwargs
    assert llamada["Bucket"] == settings.s3_bucket_name
    politica = json.loads(llamada["Policy"])
    assert politica["Statement"][0]["Action"] == ["s3:GetObject"]
    assert politica["Statement"][0]["Resource"] == [
        f"arn:aws:s3:::{settings.s3_bucket_name}/*"
    ]


@patch("app.storage_init.boto3.client")
def test_reutiliza_bucket_existente(crear_cliente: Mock) -> None:
    cliente = crear_cliente.return_value
    cliente.create_bucket.side_effect = ClientError(
        {"Error": {"Code": "BucketAlreadyOwnedByYou", "Message": "exists"}},
        "CreateBucket",
    )

    preparar_bucket()

    cliente.put_bucket_policy.assert_called_once()
