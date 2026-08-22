from collections.abc import Iterator
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.modules.imagenes.dependencies import obtener_imagen_service
from app.modules.imagenes.exceptions import ImagenNoEncontradaError
from app.modules.imagenes.schemas import ImagenApiRespuesta
from app.modules.usuarios.audit import obtener_auditoria
from app.modules.usuarios.dependencies import obtener_autenticacion, verificar_csrf

client = TestClient(app)


class ServiceFalso:
    def __init__(self) -> None:
        self.agregada: dict[str, object] | None = None
        self.imagen = SimpleNamespace(id=5, propiedad_id=7)
        self.portada_solicitada: tuple[int, int] | None = None
        self.eliminacion_solicitada: tuple[int, int] | None = None

    def agregar(self, **datos: object) -> object:
        self.agregada = datos
        return self.imagen

    def establecer_portada(self, propiedad_id: int, imagen_id: int) -> object:
        self.portada_solicitada = (propiedad_id, imagen_id)
        if propiedad_id != self.imagen.propiedad_id or imagen_id != self.imagen.id:
            raise ImagenNoEncontradaError("No existe la imagen en esa propiedad")
        return self.imagen

    def eliminar(self, propiedad_id: int, imagen_id: int) -> None:
        self.eliminacion_solicitada = (propiedad_id, imagen_id)
        if propiedad_id != self.imagen.propiedad_id or imagen_id != self.imagen.id:
            raise ImagenNoEncontradaError("No existe la imagen en esa propiedad")

    def respuesta(self, _imagen: object) -> ImagenApiRespuesta:
        return ImagenApiRespuesta(
            id=5,
            propiedad_id=7,
            nombre_original="fachada.jpg",
            mime_type="image/jpeg",
            tamanio_bytes=1000,
            ancho=800,
            alto=600,
            orden=0,
            es_portada=True,
            creado_en=datetime.now(UTC),
            url="https://storage.example/imagen",
            url_thumbnail="https://storage.example/thumbnail",
        )


class AuditoriaFalsa:
    def __init__(self) -> None:
        self.registro: dict[str, object] | None = None

    def registrar(self, **datos: object) -> object:
        self.registro = datos
        return SimpleNamespace(id=1)


@pytest.fixture
def api_imagenes() -> Iterator[tuple[ServiceFalso, AuditoriaFalsa]]:
    service = ServiceFalso()
    auditoria = AuditoriaFalsa()
    usuario = SimpleNamespace(id=1, email="operador@example.com")
    autenticacion = (SimpleNamespace(id=1), usuario)
    app.dependency_overrides[obtener_imagen_service] = lambda: service
    app.dependency_overrides[obtener_autenticacion] = lambda: autenticacion
    app.dependency_overrides[verificar_csrf] = lambda: autenticacion
    app.dependency_overrides[obtener_auditoria] = lambda: auditoria
    yield service, auditoria
    app.dependency_overrides.clear()


def test_api_imagenes_requiere_autenticacion() -> None:
    app.dependency_overrides.clear()
    respuesta = client.get("/api/v1/propiedades/7/imagenes")
    assert respuesta.status_code == 401


def test_api_carga_imagen_y_registra_auditoria(
    api_imagenes: tuple[ServiceFalso, AuditoriaFalsa],
) -> None:
    service, auditoria = api_imagenes
    respuesta = client.post(
        "/api/v1/propiedades/7/imagenes",
        files={"archivo": ("fachada.jpg", b"contenido", "image/jpeg")},
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["url_thumbnail"].startswith("https://")
    assert service.agregada is not None
    assert service.agregada["propiedad_id"] == 7
    assert service.agregada["mime_type_declarado"] == "image/jpeg"
    assert auditoria.registro is not None
    assert auditoria.registro["accion"] == "imagen.creada"


def test_api_portada_no_expone_imagen_de_otra_propiedad(
    api_imagenes: tuple[ServiceFalso, AuditoriaFalsa],
) -> None:
    service, auditoria = api_imagenes

    respuesta = client.put("/api/v1/propiedades/99/imagenes/5/portada")

    assert respuesta.status_code == 404
    assert service.portada_solicitada == (99, 5)
    assert auditoria.registro is None


def test_api_eliminar_no_expone_imagen_de_otra_propiedad(
    api_imagenes: tuple[ServiceFalso, AuditoriaFalsa],
) -> None:
    service, auditoria = api_imagenes

    respuesta = client.delete("/api/v1/propiedades/99/imagenes/5")

    assert respuesta.status_code == 404
    assert service.eliminacion_solicitada == (99, 5)
    assert auditoria.registro is None
