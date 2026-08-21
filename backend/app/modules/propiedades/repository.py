from decimal import Decimal

from sqlalchemy import ColumnElement, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.propiedades.exceptions import (
    PersistenciaPropiedadError,
    PropiedadDuplicadaError,
)
from app.modules.propiedades.models import Propiedad
from app.modules.propiedades.schemas import (
    PropiedadActualizar,
    PropiedadAdminActualizar,
    PropiedadCrear,
)


class PropiedadRepository:
    """Acceso transaccional a la persistencia de propiedades."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def crear(self, datos: PropiedadCrear, *, slug: str) -> Propiedad:
        self._validar_unicidad(codigo=datos.codigo, slug=slug)

        propiedad = Propiedad(
            **datos.model_dump(),
            slug=slug,
        )
        self.session.add(propiedad)
        self._confirmar()
        self.session.refresh(propiedad)
        return propiedad

    def obtener_por_id(self, propiedad_id: int) -> Propiedad | None:
        return self.session.get(Propiedad, propiedad_id)

    def obtener_por_slug(self, slug: str) -> Propiedad | None:
        consulta = select(Propiedad).where(Propiedad.slug == slug)
        return self.session.scalar(consulta)

    def obtener_publicada_por_slug(self, slug: str) -> Propiedad | None:
        consulta = select(Propiedad).where(
            Propiedad.slug == slug,
            Propiedad.estado == "publicada",
        )
        return self.session.scalar(consulta)

    def listar(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Propiedad], int]:
        if offset < 0:
            raise ValueError("offset no puede ser negativo")
        if not 1 <= limit <= 100:
            raise ValueError("limit debe estar entre 1 y 100")

        consulta = (
            select(Propiedad)
            .order_by(Propiedad.creado_en.desc(), Propiedad.id.desc())
            .offset(offset)
            .limit(limit)
        )
        total = self.session.scalar(select(func.count()).select_from(Propiedad))
        propiedades = list(self.session.scalars(consulta))
        return propiedades, total or 0

    def listar_publicadas(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        tipo_operacion: str | None = None,
        tipo_propiedad: str | None = None,
        localidad: str | None = None,
        precio_min: Decimal | None = None,
        precio_max: Decimal | None = None,
        dormitorios_min: int | None = None,
        destacada: bool | None = None,
    ) -> tuple[list[Propiedad], int]:
        if offset < 0:
            raise ValueError("offset no puede ser negativo")
        if not 1 <= limit <= 100:
            raise ValueError("limit debe estar entre 1 y 100")
        if (
            precio_min is not None
            and precio_max is not None
            and precio_min > precio_max
        ):
            raise ValueError("precio_min no puede superar precio_max")

        condiciones: list[ColumnElement[bool]] = [Propiedad.estado == "publicada"]
        if tipo_operacion is not None:
            condiciones.append(Propiedad.tipo_operacion == tipo_operacion)
        if tipo_propiedad is not None:
            condiciones.append(Propiedad.tipo_propiedad == tipo_propiedad)
        if localidad is not None:
            condiciones.append(Propiedad.localidad == localidad)
        if precio_min is not None:
            condiciones.append(Propiedad.precio >= precio_min)
        if precio_max is not None:
            condiciones.append(Propiedad.precio <= precio_max)
        if dormitorios_min is not None:
            condiciones.append(Propiedad.dormitorios >= dormitorios_min)
        if destacada is not None:
            condiciones.append(Propiedad.destacada == destacada)

        consulta = (
            select(Propiedad)
            .where(*condiciones)
            .order_by(
                Propiedad.destacada.desc(),
                Propiedad.creado_en.desc(),
                Propiedad.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )
        total = self.session.scalar(
            select(func.count()).select_from(Propiedad).where(*condiciones)
        )
        propiedades = list(self.session.scalars(consulta))
        return propiedades, total or 0

    def actualizar(
        self,
        propiedad: Propiedad,
        cambios: PropiedadActualizar | PropiedadAdminActualizar,
    ) -> Propiedad:
        datos = cambios.model_dump(exclude_unset=True)
        if not datos:
            return propiedad

        self._validar_unicidad(
            codigo=datos.get("codigo"),
            excluir_id=propiedad.id,
        )

        for campo, valor in datos.items():
            setattr(propiedad, campo, valor)

        self._confirmar()
        self.session.refresh(propiedad)
        return propiedad

    def existe_codigo(self, codigo: str, *, excluir_id: int | None = None) -> bool:
        consulta = select(Propiedad.id).where(Propiedad.codigo == codigo)
        if excluir_id is not None:
            consulta = consulta.where(Propiedad.id != excluir_id)
        return self.session.scalar(consulta.limit(1)) is not None

    def existe_slug(self, slug: str, *, excluir_id: int | None = None) -> bool:
        consulta = select(Propiedad.id).where(Propiedad.slug == slug)
        if excluir_id is not None:
            consulta = consulta.where(Propiedad.id != excluir_id)
        return self.session.scalar(consulta.limit(1)) is not None

    def _validar_unicidad(
        self,
        *,
        codigo: object | None = None,
        slug: object | None = None,
        excluir_id: int | None = None,
    ) -> None:
        if isinstance(codigo, str) and self.existe_codigo(
            codigo, excluir_id=excluir_id
        ):
            raise PropiedadDuplicadaError("codigo")
        if isinstance(slug, str) and self.existe_slug(slug, excluir_id=excluir_id):
            raise PropiedadDuplicadaError("slug")

    def _confirmar(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            campo = self._campo_unico_desde_error(error)
            if campo is not None:
                raise PropiedadDuplicadaError(campo) from error
            raise PersistenciaPropiedadError(
                "La base de datos rechazó la operación"
            ) from error

    @staticmethod
    def _campo_unico_desde_error(error: IntegrityError) -> str | None:
        diagnostico = getattr(error.orig, "diag", None)
        constraint = getattr(diagnostico, "constraint_name", "") or ""
        if "codigo" in constraint:
            return "codigo"
        if "slug" in constraint:
            return "slug"
        return None
