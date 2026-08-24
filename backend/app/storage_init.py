import json

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from app.core.config import settings


def preparar_bucket() -> None:
    cliente = boto3.client(
        "s3",
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        region_name=settings.s3_region,
        use_ssl=settings.s3_use_ssl,
    )
    try:
        cliente.create_bucket(Bucket=settings.s3_bucket_name)
    except ClientError as error:
        codigo = error.response.get("Error", {}).get("Code")
        if codigo not in {"BucketAlreadyExists", "BucketAlreadyOwnedByYou"}:
            raise

    politica = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{settings.s3_bucket_name}/*"],
            }
        ],
    }
    cliente.put_bucket_policy(
        Bucket=settings.s3_bucket_name,
        Policy=json.dumps(politica),
    )


if __name__ == "__main__":
    preparar_bucket()
