from collections.abc import Iterator
from typing import cast
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.modules.propiedades.models import Propiedad
from app.modules.usuarios.models import RegistroAuditoria, SesionUsuario, Usuario
from app.modules.usuarios.repository import UsuarioRepository
from app.modules.usuarios.schemas import UsuarioCrear
from app.modules.usuarios.service import UsuarioService

client = TestClient(app, base_url="https://testserver")


@pytest.fixture(autouse=True)
def autenticar_administrador() -> Iterator[None]:
    identificador = uuid4().hex[:10]
    with SessionLocal() as session:
        usuario = UsuarioService(UsuarioRepository(session)).crear(
            UsuarioCrear(
                email=f"test-public-admin-{identificador}@example.com",
                nombre="Administrador público",
                contrasena="contrasena-segura-pruebas",
                rol="administrador",
            )
        )
        usuario_id = usuario.id

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": usuario.email,
            "contrasena": "contrasena-segura-pruebas",
        },
    )
    assert login.status_code == 200
    csrf = client.cookies.get("tophouse_csrf")
    assert csrf is not None
    client.headers["X-CSRF-Token"] = csrf

    yield

    client.cookies.clear()
    client.headers.pop("X-CSRF-Token", None)
    with SessionLocal() as session:
        session.execute(
            delete(RegistroAuditoria).where(RegistroAuditoria.usuario_id == usuario_id)
        )
        session.execute(
            delete(SesionUsuario).where(SesionUsuario.usuario_id == usuario_id)
        )
        session.execute(delete(Usuario).where(Usuario.id == usuario_id))
        session.commit()


@pytest.fixture
def limpiar_propiedades_publicas() -> Iterator[None]:
    yield
    with SessionLocal() as session:
        session.execute(delete(Propiedad).where(Propiedad.codigo.like("TEST-PUBLIC-%")))
        session.commit()


def crear_propiedad(
    *,
    publicada: bool,
    tipo_operacion: str = "venta",
    tipo_propiedad: str = "casa",
    localidad: str = "Asunción",
    precio: str = "150000.00",
    dormitorios: int = 3,
    destacada: bool = False,
) -> dict[str, object]:
    identificador = uuid4().hex[:10]
    datos: dict[str, object] = {
        "codigo": f"TEST-PUBLIC-{identificador}",
        "titulo": f"Propiedad pública {identificador}",
        "descripcion": "Registro temporal para probar privacidad",
        "tipo_operacion": tipo_operacion,
        "tipo_propiedad": tipo_propiedad,
        "precio": precio,
        "moneda": "USD",
        "localidad": localidad,
        "direccion": "Av. Confidencial 123",
        "latitud": "-25.300000",
        "longitud": "-57.630000",
        "mostrar_ubicacion_exacta": True,
        "dormitorios": dormitorios,
    }
    creada = client.post("/api/v1/propiedades", json=datos).json()
    if publicada:
        creada = client.patch(
            f"/api/v1/propiedades/{creada['id']}/admin",
            json={"estado": "publicada", "destacada": destacada},
        ).json()
    return cast(dict[str, object], creada)


def assert_sin_ubicacion_privada(datos: dict[str, object]) -> None:
    assert "direccion" not in datos
    assert "latitud" not in datos
    assert "longitud" not in datos
    assert "mostrar_ubicacion_exacta" not in datos


def test_api_publica_solo_lista_publicadas_y_oculta_ubicacion(
    limpiar_propiedades_publicas: None,
) -> None:
    publicada = crear_propiedad(publicada=True)
    borrador = crear_propiedad(publicada=False)

    respuesta = client.get("/api/v1/publico/propiedades?limit=100")

    assert respuesta.status_code == 200
    items = respuesta.json()["items"]
    ids = {item["id"] for item in items}
    assert publicada["id"] in ids
    assert borrador["id"] not in ids
    item_publicado = next(item for item in items if item["id"] == publicada["id"])
    assert_sin_ubicacion_privada(item_publicado)
    assert item_publicado["imagenes"] == []


def test_api_publica_detalle_por_slug_sin_ubicacion(
    limpiar_propiedades_publicas: None,
) -> None:
    publicada = crear_propiedad(publicada=True)

    respuesta = client.get(f"/api/v1/publico/propiedades/{publicada['slug']}")

    assert respuesta.status_code == 200
    assert respuesta.json()["id"] == publicada["id"]
    assert_sin_ubicacion_privada(respuesta.json())
    assert respuesta.json()["imagenes"] == []


def test_api_publica_no_expone_borrador_por_slug(
    limpiar_propiedades_publicas: None,
) -> None:
    borrador = crear_propiedad(publicada=False)

    respuesta = client.get(f"/api/v1/publico/propiedades/{borrador['slug']}")

    assert respuesta.status_code == 404


def test_api_publica_aplica_filtros(
    limpiar_propiedades_publicas: None,
) -> None:
    coincidente = crear_propiedad(
        publicada=True,
        tipo_operacion="alquiler",
        tipo_propiedad="departamento",
        localidad="Luque",
        precio="800.00",
        dormitorios=2,
        destacada=True,
    )
    crear_propiedad(publicada=True, tipo_operacion="venta")

    respuesta = client.get(
        "/api/v1/publico/propiedades",
        params={
            "tipo_operacion": "alquiler",
            "tipo_propiedad": "departamento",
            "localidad": "Luque",
            "precio_min": "700",
            "precio_max": "900",
            "dormitorios_min": 2,
            "destacada": True,
        },
    )

    assert respuesta.status_code == 200
    items = respuesta.json()["items"]
    assert [item["id"] for item in items] == [coincidente["id"]]


def test_api_publica_rechaza_rango_de_precio_invertido(
    limpiar_propiedades_publicas: None,
) -> None:
    crear_propiedad(publicada=True)

    respuesta = client.get("/api/v1/publico/propiedades?precio_min=1000&precio_max=500")

    assert respuesta.status_code == 400
