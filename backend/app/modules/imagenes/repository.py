from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.modules.imagenes.models import ImagenPropiedad
from app.modules.imagenes.schemas import ImagenMetadatosCrear


class ImagenRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def contar(self, propiedad_id: int) -> int:
        consulta = select(func.count()).where(
            ImagenPropiedad.propiedad_id == propiedad_id
        )
        return self.session.scalar(consulta) or 0

    def siguiente_orden(self, propiedad_id: int) -> int:
        consulta = select(func.max(ImagenPropiedad.orden)).where(
            ImagenPropiedad.propiedad_id == propiedad_id
        )
        maximo = self.session.scalar(consulta)
        return 0 if maximo is None else maximo + 1

    def crear(
        self,
        propiedad_id: int,
        datos: ImagenMetadatosCrear,
    ) -> ImagenPropiedad:
        imagen = ImagenPropiedad(propiedad_id=propiedad_id, **datos.model_dump())
        self.session.add(imagen)
        try:
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            raise
        self.session.refresh(imagen)
        return imagen

    def listar(self, propiedad_id: int) -> list[ImagenPropiedad]:
        consulta = (
            select(ImagenPropiedad)
            .where(ImagenPropiedad.propiedad_id == propiedad_id)
            .order_by(ImagenPropiedad.orden, ImagenPropiedad.id)
        )
        return list(self.session.scalars(consulta))

    def obtener(self, imagen_id: int) -> ImagenPropiedad | None:
        return self.session.get(ImagenPropiedad, imagen_id)

    def eliminar(self, imagen: ImagenPropiedad) -> None:
        self.session.delete(imagen)
        self.session.commit()

    def reordenar(self, imagenes: list[ImagenPropiedad]) -> None:
        desplazamiento = max((imagen.orden for imagen in imagenes), default=-1) + 1
        for indice, imagen in enumerate(imagenes):
            imagen.orden = desplazamiento + indice
        self.session.flush()
        for indice, imagen in enumerate(imagenes):
            imagen.orden = indice
        self.session.commit()

    def establecer_portada(
        self,
        imagenes: list[ImagenPropiedad],
        portada: ImagenPropiedad,
    ) -> None:
        for imagen in imagenes:
            imagen.es_portada = False
        self.session.flush()
        portada.es_portada = True
        self.session.commit()
