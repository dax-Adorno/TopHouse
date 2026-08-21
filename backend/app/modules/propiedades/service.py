from app.modules.propiedades.exceptions import (
    GeneracionSlugError,
    PropiedadNoEncontradaError,
    TransicionEstadoInvalidaError,
)
from app.modules.propiedades.models import Propiedad
from app.modules.propiedades.repository import PropiedadRepository
from app.modules.propiedades.schemas import (
    EstadoPropiedad,
    PropiedadActualizar,
    PropiedadAdminActualizar,
    PropiedadCrear,
)
from app.modules.propiedades.slug import normalizar_slug, slug_con_sufijo

TRANSICIONES_ESTADO: dict[EstadoPropiedad, frozenset[EstadoPropiedad]] = {
    EstadoPropiedad.BORRADOR: frozenset(
        {
            EstadoPropiedad.PUBLICADA,
            EstadoPropiedad.NO_DISPONIBLE,
        }
    ),
    EstadoPropiedad.PUBLICADA: frozenset(
        {
            EstadoPropiedad.PAUSADA,
            EstadoPropiedad.RESERVADA,
            EstadoPropiedad.ALQUILADA,
            EstadoPropiedad.VENDIDA,
            EstadoPropiedad.NO_DISPONIBLE,
        }
    ),
    EstadoPropiedad.PAUSADA: frozenset(
        {
            EstadoPropiedad.PUBLICADA,
            EstadoPropiedad.NO_DISPONIBLE,
        }
    ),
    EstadoPropiedad.RESERVADA: frozenset(
        {
            EstadoPropiedad.PUBLICADA,
            EstadoPropiedad.ALQUILADA,
            EstadoPropiedad.VENDIDA,
            EstadoPropiedad.NO_DISPONIBLE,
        }
    ),
    EstadoPropiedad.ALQUILADA: frozenset(
        {
            EstadoPropiedad.PUBLICADA,
            EstadoPropiedad.NO_DISPONIBLE,
        }
    ),
    EstadoPropiedad.VENDIDA: frozenset({EstadoPropiedad.NO_DISPONIBLE}),
    EstadoPropiedad.NO_DISPONIBLE: frozenset({EstadoPropiedad.BORRADOR}),
}


class PropiedadService:
    """Orquesta reglas de negocio y persistencia de Propiedades."""

    def __init__(self, repository: PropiedadRepository) -> None:
        self.repository = repository

    def crear(self, datos: PropiedadCrear) -> Propiedad:
        slug = self._generar_slug_unico(datos.titulo)
        return self.repository.crear(datos, slug=slug)

    def obtener_por_id(self, propiedad_id: int) -> Propiedad:
        propiedad = self.repository.obtener_por_id(propiedad_id)
        if propiedad is None:
            raise PropiedadNoEncontradaError(
                f"No existe la propiedad con id {propiedad_id}"
            )
        return propiedad

    def obtener_por_slug(self, slug: str) -> Propiedad:
        propiedad = self.repository.obtener_por_slug(slug)
        if propiedad is None:
            raise PropiedadNoEncontradaError(f"No existe la propiedad con slug {slug}")
        return propiedad

    def listar(
        self, *, offset: int = 0, limit: int = 20
    ) -> tuple[list[Propiedad], int]:
        return self.repository.listar(offset=offset, limit=limit)

    def actualizar(
        self,
        propiedad_id: int,
        cambios: PropiedadActualizar,
    ) -> Propiedad:
        propiedad = self.obtener_por_id(propiedad_id)
        return self.repository.actualizar(propiedad, cambios)

    def actualizar_admin(
        self,
        propiedad_id: int,
        cambios: PropiedadAdminActualizar,
    ) -> Propiedad:
        propiedad = self.obtener_por_id(propiedad_id)
        if cambios.estado is not None:
            self._validar_transicion_estado(propiedad.estado, cambios.estado)
        return self.repository.actualizar(propiedad, cambios)

    def _generar_slug_unico(self, titulo: str) -> str:
        base = normalizar_slug(titulo)
        if not self.repository.existe_slug(base):
            return base

        for numero in range(2, 10_000):
            candidato = slug_con_sufijo(base, numero)
            if not self.repository.existe_slug(candidato):
                return candidato

        raise GeneracionSlugError(
            "No fue posible generar un slug único después de 9999 intentos"
        )

    @staticmethod
    def _validar_transicion_estado(
        estado_actual: str,
        estado_nuevo: EstadoPropiedad,
    ) -> None:
        actual = EstadoPropiedad(estado_actual)
        if actual == estado_nuevo:
            return
        if estado_nuevo not in TRANSICIONES_ESTADO[actual]:
            raise TransicionEstadoInvalidaError(actual.value, estado_nuevo.value)
