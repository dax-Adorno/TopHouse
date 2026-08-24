from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_env: str = "development"
    debug: bool = False

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    session_duration_hours: int = 12
    session_cookie_secure: bool = True
    cors_origins: str = "http://localhost:5173"
    allowed_hosts: str = "localhost,127.0.0.1,testserver"

    s3_endpoint_url: str | None = None
    s3_access_key_id: str | None = None
    s3_secret_access_key: str | None = None
    s3_bucket_name: str = "tophouse-properties"
    s3_region: str = "auto"
    s3_use_ssl: bool = True
    s3_public_base_url: str | None = None

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )

    @property
    def cors_allowed_origins(self) -> list[str]:
        return [
            origin.strip() for origin in self.cors_origins.split(",") if origin.strip()
        ]

    @property
    def trusted_hosts(self) -> list[str]:
        return [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @model_validator(mode="after")
    def validar_produccion(self) -> Self:
        if not self.is_production:
            return self
        if self.debug:
            raise ValueError("DEBUG debe estar desactivado en producción")
        if not self.session_cookie_secure:
            raise ValueError("SESSION_COOKIE_SECURE debe estar activo en producción")
        if not self.cors_allowed_origins or any(
            not origin.startswith("https://") for origin in self.cors_allowed_origins
        ):
            raise ValueError("CORS_ORIGINS debe contener únicamente orígenes HTTPS")
        if not self.trusted_hosts or "*" in self.trusted_hosts:
            raise ValueError("ALLOWED_HOSTS debe enumerar hosts de producción")
        return self


settings = Settings()
