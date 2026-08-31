from unittest.mock import patch

from app.core.health import comprobar_dependencias


@patch("app.core.health.comprobar_almacenamiento")
@patch("app.core.health.comprobar_base_datos")
def test_comprueba_todas_las_dependencias(
    comprobar_base_datos_mock: object,
    comprobar_almacenamiento_mock: object,
) -> None:
    assert comprobar_dependencias() == {
        "database": "ok",
        "storage": "ok",
    }


@patch("app.core.health.comprobar_almacenamiento")
@patch("app.core.health.comprobar_base_datos", side_effect=RuntimeError)
def test_aisla_fallos_de_dependencias(
    comprobar_base_datos_mock: object,
    comprobar_almacenamiento_mock: object,
) -> None:
    assert comprobar_dependencias() == {
        "database": "unavailable",
        "storage": "ok",
    }
