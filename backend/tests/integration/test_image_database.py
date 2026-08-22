from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.database import SessionLocal
from app.modules.imagenes.models import ImagenPropiedad
from app.modules.propiedades.models import Propiedad


def test_base_impide_dos_portadas_por_propiedad() -> None:
    identificador = uuid4().hex[:10]
    with SessionLocal() as session:
        propiedad = Propiedad(
            codigo=f"TEST-IMG-{identificador}",
            slug=f"test-img-{identificador}",
            titulo="Propiedad para imágenes",
            descripcion="Registro temporal",
            tipo_operacion="venta",
            tipo_propiedad="casa",
            localidad="Merlo",
        )
        session.add(propiedad)
        session.flush()
        session.add(
            ImagenPropiedad(
                propiedad_id=propiedad.id,
                clave_objeto=f"{identificador}/uno.webp",
                clave_thumbnail=f"{identificador}/uno-thumb.webp",
                nombre_original="uno.jpg",
                mime_type="image/jpeg",
                tamanio_bytes=100_000,
                ancho=1200,
                alto=800,
                orden=0,
                es_portada=True,
            )
        )
        session.commit()
        session.add(
            ImagenPropiedad(
                propiedad_id=propiedad.id,
                clave_objeto=f"{identificador}/dos.webp",
                clave_thumbnail=f"{identificador}/dos-thumb.webp",
                nombre_original="dos.jpg",
                mime_type="image/jpeg",
                tamanio_bytes=100_000,
                ancho=1200,
                alto=800,
                orden=1,
                es_portada=True,
            )
        )

        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        session.delete(propiedad)
        session.commit()
