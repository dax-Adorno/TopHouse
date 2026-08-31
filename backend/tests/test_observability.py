import json
import logging
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from app.core.observability import JsonFormatter, obtener_request_id
from app.main import app

client = TestClient(app)


def test_formatter_emite_json_estructurado() -> None:
    record = logging.LogRecord(
        name="tophouse.requests",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "request-123"
    record.status_code = 200

    evento = json.loads(JsonFormatter().format(record))

    assert evento["level"] == "INFO"
    assert evento["message"] == "request_completed"
    assert evento["request_id"] == "request-123"
    assert evento["status_code"] == 200
    assert "timestamp" in evento


def test_request_id_rechaza_valores_no_seguros() -> None:
    request_id = obtener_request_id("valor con espacios\ny otra linea")

    assert request_id != "valor con espacios\ny otra linea"
    assert len(request_id) == 36


@patch("app.core.observability.request_logger.info")
def test_middleware_agrega_request_id_y_registra_solicitud(logger_info: Mock) -> None:
    response = client.get(
        "/health?token=no-debe-aparecer",
        headers={"X-Request-ID": "browser-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "browser-123"
    contexto = logger_info.call_args.kwargs["extra"]
    assert contexto["request_id"] == "browser-123"
    assert contexto["method"] == "GET"
    assert contexto["path"] == "/health"
    assert contexto["status_code"] == 200
    assert contexto["duration_ms"] >= 0
