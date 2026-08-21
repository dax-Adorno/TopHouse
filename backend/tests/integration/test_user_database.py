import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.core.database import engine


def test_usuarios_table_and_columns_exist() -> None:
    inspector = inspect(engine)

    assert "usuarios" in inspector.get_table_names()
    columnas = {columna["name"] for columna in inspector.get_columns("usuarios")}
    assert columnas == {
        "id",
        "email",
        "nombre",
        "password_hash",
        "rol",
        "activo",
        "ultimo_acceso_en",
        "creado_en",
        "actualizado_en",
    }


def test_usuarios_constraints_and_indexes_exist() -> None:
    inspector = inspect(engine)

    constraints = {
        constraint["name"] for constraint in inspector.get_check_constraints("usuarios")
    }
    indexes = {index["name"]: index for index in inspector.get_indexes("usuarios")}

    assert "ck_usuarios_rol" in constraints
    assert indexes["ix_usuarios_email"]["unique"] is True
    assert "ix_usuarios_activo" in indexes
    assert "ix_usuarios_rol" in indexes


def test_usuario_defaults_are_secure() -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            resultado = connection.execute(
                text("""
                    INSERT INTO usuarios (email, nombre, password_hash)
                    VALUES (:email, :nombre, :password_hash)
                    RETURNING rol, activo
                    """),
                {
                    "email": "test-defaults@tophouse.invalid",
                    "nombre": "Usuario de prueba",
                    "password_hash": "hash-no-real",
                },
            ).one()

            assert resultado.rol == "operador"
            assert resultado.activo is True
        finally:
            transaction.rollback()


def test_usuarios_rechaza_rol_invalido() -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            with pytest.raises(IntegrityError):
                connection.execute(
                    text("""
                        INSERT INTO usuarios (
                            email, nombre, password_hash, rol
                        )
                        VALUES (
                            :email, :nombre, :password_hash, :rol
                        )
                        """),
                    {
                        "email": "test-role@tophouse.invalid",
                        "nombre": "Usuario de prueba",
                        "password_hash": "hash-no-real",
                        "rol": "superusuario",
                    },
                )
        finally:
            transaction.rollback()


def test_usuarios_rechaza_email_duplicado() -> None:
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            datos = {
                "email": "test-unique@tophouse.invalid",
                "nombre": "Usuario de prueba",
                "password_hash": "hash-no-real",
            }
            connection.execute(
                text("""
                    INSERT INTO usuarios (email, nombre, password_hash)
                    VALUES (:email, :nombre, :password_hash)
                    """),
                datos,
            )

            with pytest.raises(IntegrityError):
                connection.execute(
                    text("""
                        INSERT INTO usuarios (email, nombre, password_hash)
                        VALUES (:email, :nombre, :password_hash)
                        """),
                    datos,
                )
        finally:
            transaction.rollback()
