import json
import logging
import re
import sys
import time
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
request_logger = logging.getLogger("tophouse.requests")


class JsonFormatter(logging.Formatter):
    """Serializa eventos operativos en JSON, una línea por registro."""

    def format(self, record: logging.LogRecord) -> str:
        evento: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for campo in (
            "request_id",
            "method",
            "path",
            "status_code",
            "duration_ms",
        ):
            if hasattr(record, campo):
                evento[campo] = getattr(record, campo)
        if record.exc_info:
            evento["exception"] = self.formatException(record.exc_info)
        return json.dumps(evento, ensure_ascii=False, default=str)


def configurar_logging(level: str) -> None:
    """Configura los logs propios sin alterar los logs internos de librerías."""
    logger = logging.getLogger("tophouse")
    logger.setLevel(level.upper())
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)


def obtener_request_id(valor_recibido: str | None) -> str:
    if valor_recibido and REQUEST_ID_PATTERN.fullmatch(valor_recibido):
        return valor_recibido
    return str(uuid4())


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Registra una entrada estructurada por solicitud sin query strings."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = obtener_request_id(request.headers.get(REQUEST_ID_HEADER))
        inicio = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            request_logger.exception(
                "request_failed",
                extra=self._contexto(request, request_id, 500, inicio),
            )
            raise
        response.headers[REQUEST_ID_HEADER] = request_id
        request_logger.info(
            "request_completed",
            extra=self._contexto(
                request,
                request_id,
                response.status_code,
                inicio,
            ),
        )
        return response

    @staticmethod
    def _contexto(
        request: Request,
        request_id: str,
        status_code: int,
        inicio: float,
    ) -> dict[str, object]:
        return {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "duration_ms": round((time.perf_counter() - inicio) * 1000, 2),
        }
