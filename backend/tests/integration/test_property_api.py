from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.core.database import SessionLocal
from app.main import app
from app.modules.propiedades.models import Propiedad

client = TestClient(app)


@pytest.fixture
def limpiar_propiedades_api() -> Iterator[None]:
    yield
    with SessionLocal() as session:
        session.execute(delete(Propiedad).where(Propiedad.codigo.like("TEST-API-%")))
        session.commit()


@pytest.fixture
def datos_propiedad() -> dict[str, object]:
    identificador = uuid4().hex[:10]
    return {
        "codigo": f"TEST-API-{identificador}",
        "titulo": f"Casa API {identificador}",
        "descripcion": "Propiedad temporal para probar la API",
        "tipo_operacion": "venta",
        "tipo_propiedad": "casa",
        "precio": "175000.00",
        "moneda": "USD",
        "localidad": "Asunción",
        "latitud": "-25.300000",
        "longitud": "-57.630000",
    }


def test_api_crea_y_consulta_propiedad(
    limpiar_propiedades_api: None,
    datos_propiedad: dict[str, object],
) -> None:
    respuesta_crear = client.post("/api/v1/propiedades", json=datos_propiedad)

    assert respuesta_crear.status_code == 201
    creada = respuesta_crear.json()
    assert creada["codigo"] == datos_propiedad["codigo"]
    assert creada["estado"] == "borrador"
    assert creada["destacada"] is False

    respuesta_id = client.get(f"/api/v1/propiedades/{creada['id']}")
    respuesta_slug = client.get(f"/api/v1/propiedades/slug/{creada['slug']}")

    assert respuesta_id.status_code == 200
    assert respuesta_id.json()["id"] == creada["id"]
    assert respuesta_slug.status_code == 200
    assert respuesta_slug.json()["slug"] == creada["slug"]


def test_api_lista_propiedades_paginadas(
    limpiar_propiedades_api: None,
    datos_propiedad: dict[str, object],
) -> None:
    creada = client.post("/api/v1/propiedades", json=datos_propiedad).json()

    respuesta = client.get("/api/v1/propiedades?offset=0&limit=100")

    assert respuesta.status_code == 200
    pagina = respuesta.json()
    assert pagina["offset"] == 0
    assert pagina["limit"] == 100
    assert pagina["total"] >= 1
    assert creada["id"] in {item["id"] for item in pagina["items"]}


def test_api_actualiza_campos_y_estado(
    limpiar_propiedades_api: None,
    datos_propiedad: dict[str, object],
) -> None:
    creada = client.post("/api/v1/propiedades", json=datos_propiedad).json()

    respuesta_patch = client.patch(
        f"/api/v1/propiedades/{creada['id']}",
        json={"titulo": "Título actualizado"},
    )
    respuesta_estado = client.patch(
        f"/api/v1/propiedades/{creada['id']}/admin",
        json={"estado": "publicada", "destacada": True},
    )

    assert respuesta_patch.status_code == 200
    assert respuesta_patch.json()["titulo"] == "Título actualizado"
    assert respuesta_estado.status_code == 200
    assert respuesta_estado.json()["estado"] == "publicada"
    assert respuesta_estado.json()["destacada"] is True


def test_api_rechaza_codigo_duplicado(
    limpiar_propiedades_api: None,
    datos_propiedad: dict[str, object],
) -> None:
    primera = client.post("/api/v1/propiedades", json=datos_propiedad)
    datos_duplicados = {
        **datos_propiedad,
        "titulo": "Otra propiedad",
    }

    segunda = client.post("/api/v1/propiedades", json=datos_duplicados)

    assert primera.status_code == 201
    assert segunda.status_code == 409
    assert segunda.json()["campo"] == "codigo"


def test_api_devuelve_404_para_propiedad_inexistente() -> None:
    respuesta = client.get("/api/v1/propiedades/999999999")

    assert respuesta.status_code == 404


def test_api_rechaza_transicion_invalida(
    limpiar_propiedades_api: None,
    datos_propiedad: dict[str, object],
) -> None:
    creada = client.post("/api/v1/propiedades", json=datos_propiedad).json()

    respuesta = client.patch(
        f"/api/v1/propiedades/{creada['id']}/admin",
        json={"estado": "vendida"},
    )

    assert respuesta.status_code == 409
    assert respuesta.json()["estado_actual"] == "borrador"
    assert respuesta.json()["estado_nuevo"] == "vendida"


@pytest.mark.parametrize(
    "query",
    ["offset=-1", "limit=0", "limit=101"],
)
def test_api_valida_paginacion(query: str) -> None:
    respuesta = client.get(f"/api/v1/propiedades?{query}")

    assert respuesta.status_code == 422
