from dataclasses import dataclass
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.modules.propiedades.models import Propiedad
from app.modules.usuarios.models import Usuario
from app.modules.usuarios.passwords import hashear_contrasena


class DemoProperty(TypedDict):
    codigo: str
    slug: str
    titulo: str
    descripcion: str
    tipo_operacion: str
    tipo_propiedad: str
    precio: Decimal | None
    moneda: str | None
    localidad: str
    zona: str | None
    direccion: str | None
    latitud: Decimal | None
    longitud: Decimal | None
    mostrar_ubicacion_exacta: bool
    dormitorios: int | None
    banios: int | None
    superficie_cubierta: Decimal | None
    superficie_total: Decimal | None
    estado: str
    destacada: bool


@dataclass(frozen=True)
class SeedResult:
    created: int
    updated: int


DEMO_PROPERTIES: tuple[DemoProperty, ...] = (
    {
        "codigo": "DEMO-TH-001",
        "slug": "casa-luminosa-piedra-blanca",
        "titulo": "Casa luminosa en Piedra Blanca",
        "descripcion": (
            "Casa familiar con ambientes amplios, galeria con parrilla y jardin "
            "privado. Ideal para quienes buscan una propiedad lista para mudarse."
        ),
        "tipo_operacion": "venta",
        "tipo_propiedad": "casa",
        "precio": Decimal("245000.00"),
        "moneda": "USD",
        "localidad": "Merlo",
        "zona": "Piedra Blanca",
        "direccion": "Piedra Blanca",
        "latitud": Decimal("-32.342900"),
        "longitud": Decimal("-65.013900"),
        "mostrar_ubicacion_exacta": False,
        "dormitorios": 3,
        "banios": 3,
        "superficie_cubierta": Decimal("210.00"),
        "superficie_total": Decimal("420.00"),
        "estado": "publicada",
        "destacada": True,
    },
    {
        "codigo": "DEMO-TH-002",
        "slug": "departamento-centrico-villa-de-merlo",
        "titulo": "Departamento centrico en Villa de Merlo",
        "descripcion": (
            "Unidad con balcon, amenities y cochera. Una opcion practica para "
            "vivir cerca de servicios, comercios y espacios gastronomicos."
        ),
        "tipo_operacion": "alquiler",
        "tipo_propiedad": "departamento",
        "precio": Decimal("950.00"),
        "moneda": "USD",
        "localidad": "Villa de Merlo",
        "zona": "Centro",
        "direccion": "Centro",
        "latitud": Decimal("-32.347200"),
        "longitud": Decimal("-65.011700"),
        "mostrar_ubicacion_exacta": False,
        "dormitorios": 2,
        "banios": 2,
        "superficie_cubierta": Decimal("92.00"),
        "superficie_total": Decimal("112.00"),
        "estado": "publicada",
        "destacada": True,
    },
    {
        "codigo": "DEMO-TH-003",
        "slug": "duplex-con-patio-carpinteria",
        "titulo": "Duplex con patio en Carpinteria",
        "descripcion": (
            "Duplex de tres dormitorios con area social integrada, patio lateral "
            "y buena conexion hacia la ruta provincial."
        ),
        "tipo_operacion": "venta",
        "tipo_propiedad": "duplex",
        "precio": Decimal("138000.00"),
        "moneda": "USD",
        "localidad": "Carpinteria",
        "zona": "Centro",
        "direccion": "Carpinteria",
        "latitud": Decimal("-32.409100"),
        "longitud": Decimal("-64.988600"),
        "mostrar_ubicacion_exacta": False,
        "dormitorios": 3,
        "banios": 2,
        "superficie_cubierta": Decimal("145.00"),
        "superficie_total": Decimal("205.00"),
        "estado": "publicada",
        "destacada": False,
    },
    {
        "codigo": "DEMO-TH-004",
        "slug": "cabana-temporaria-cerro-de-oro",
        "titulo": "Cabana temporaria en Cerro de Oro",
        "descripcion": (
            "Cabana equipada para estadias cortas, con entorno tranquilo y "
            "acceso rapido a circuitos turisticos de la villa."
        ),
        "tipo_operacion": "temporario",
        "tipo_propiedad": "cabana",
        "precio": Decimal("65.00"),
        "moneda": "USD",
        "localidad": "Merlo",
        "zona": "Cerro de Oro",
        "direccion": "Cerro de Oro",
        "latitud": Decimal("-32.369500"),
        "longitud": Decimal("-65.020100"),
        "mostrar_ubicacion_exacta": False,
        "dormitorios": 1,
        "banios": 1,
        "superficie_cubierta": Decimal("38.00"),
        "superficie_total": Decimal("45.00"),
        "estado": "publicada",
        "destacada": False,
    },
    {
        "codigo": "DEMO-TH-005",
        "slug": "terreno-residencial-cortaderas",
        "titulo": "Terreno residencial en Cortaderas",
        "descripcion": (
            "Terreno nivelado en zona residencial, con frente amplio y entorno "
            "tranquilo para proyecto de vivienda o casa de descanso."
        ),
        "tipo_operacion": "venta",
        "tipo_propiedad": "terreno",
        "precio": Decimal("82000.00"),
        "moneda": "USD",
        "localidad": "Cortaderas",
        "zona": "Centro",
        "direccion": "Cortaderas",
        "latitud": Decimal("-32.507700"),
        "longitud": Decimal("-64.988100"),
        "mostrar_ubicacion_exacta": False,
        "dormitorios": None,
        "banios": None,
        "superficie_cubierta": None,
        "superficie_total": Decimal("720.00"),
        "estado": "publicada",
        "destacada": True,
    },
    {
        "codigo": "DEMO-TH-006",
        "slug": "local-comercial-avenida-del-sol",
        "titulo": "Local comercial sobre Avenida del Sol",
        "descripcion": (
            "Planta flexible para comercio o atencion al publico, con buena "
            "exposicion y circulacion durante todo el ano."
        ),
        "tipo_operacion": "alquiler",
        "tipo_propiedad": "local",
        "precio": Decimal("1800.00"),
        "moneda": "USD",
        "localidad": "Merlo",
        "zona": "Avenida del Sol",
        "direccion": "Avenida del Sol",
        "latitud": Decimal("-32.344300"),
        "longitud": Decimal("-65.012500"),
        "mostrar_ubicacion_exacta": False,
        "dormitorios": None,
        "banios": 2,
        "superficie_cubierta": Decimal("160.00"),
        "superficie_total": Decimal("180.00"),
        "estado": "publicada",
        "destacada": False,
    },
)

DEMO_PROPERTY_CODES = tuple(
    property_data["codigo"] for property_data in DEMO_PROPERTIES
)
DEMO_ADMIN_EMAIL = "admin.demo@tophouse.com"
DEMO_ADMIN_PASSWORD = "TopHouse-demo-2026"
LEGACY_DEMO_ADMIN_EMAILS = ("admin@tophouse.local",)


def seed_demo_properties(session: Session) -> SeedResult:
    created = 0
    updated = 0

    for property_data in DEMO_PROPERTIES:
        propiedad = session.scalar(
            select(Propiedad).where(Propiedad.codigo == property_data["codigo"])
        )
        if propiedad is None:
            session.add(Propiedad(**property_data))
            created += 1
            continue

        for field, value in property_data.items():
            setattr(propiedad, field, value)
        updated += 1

    return SeedResult(created=created, updated=updated)


def seed_demo_admin(session: Session) -> SeedResult:
    for legacy_email in LEGACY_DEMO_ADMIN_EMAILS:
        legacy_user = session.scalar(
            select(Usuario).where(Usuario.email == legacy_email)
        )
        if legacy_user is not None:
            session.delete(legacy_user)

    usuario = session.scalar(select(Usuario).where(Usuario.email == DEMO_ADMIN_EMAIL))
    password_hash = hashear_contrasena(DEMO_ADMIN_PASSWORD)

    if usuario is None:
        session.add(
            Usuario(
                email=DEMO_ADMIN_EMAIL,
                nombre="Administrador Demo",
                password_hash=password_hash,
                rol="administrador",
                activo=True,
            )
        )
        return SeedResult(created=1, updated=0)

    usuario.nombre = "Administrador Demo"
    usuario.password_hash = password_hash
    usuario.rol = "administrador"
    usuario.activo = True
    return SeedResult(created=0, updated=1)


def main() -> None:
    if settings.app_env == "production":
        raise RuntimeError("El seed demo no debe ejecutarse en produccion")

    with SessionLocal() as session:
        properties_result = seed_demo_properties(session)
        admin_result = seed_demo_admin(session)
        session.commit()

    print(
        "Demo properties ready: "
        f"{properties_result.created} created, {properties_result.updated} updated."
    )
    print(
        "Demo admin ready: "
        f"{admin_result.created} created, {admin_result.updated} updated."
    )
    print(f"Demo admin credentials: {DEMO_ADMIN_EMAIL} / {DEMO_ADMIN_PASSWORD}")


if __name__ == "__main__":
    main()
