import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { Link } from "react-router-dom";
import heroImage from "../assets/hero.png";
import { listPublicProperties } from "../lib/api";
import { formatArea, formatMoney, operationLabel } from "../lib/propertyFormat";
import type {
  PropertyPage,
  PublicProperty,
  PublicPropertyFilters,
} from "../types/property";

const PAGE_SIZE = 9;

const initialPage: PropertyPage = {
  items: [],
  total: 0,
  offset: 0,
  limit: PAGE_SIZE,
};

type LoadState = "loading" | "success" | "error";

type DraftFilters = {
  tipo_operacion: PublicPropertyFilters["tipo_operacion"];
  tipo_propiedad: string;
  localidad: string;
  precio_min: string;
  precio_max: string;
  dormitorios_min: string;
};

const initialFilters: DraftFilters = {
  tipo_operacion: "",
  tipo_propiedad: "",
  localidad: "",
  precio_min: "",
  precio_max: "",
  dormitorios_min: "",
};

function buildFilters(
  filters: DraftFilters,
  offset: number,
): PublicPropertyFilters {
  return {
    ...filters,
    offset,
    limit: PAGE_SIZE,
  };
}

function PropertyCard({ property }: { property: PublicProperty }) {
  const cover = property.imagenes.find((image) => image.es_portada);
  const image = cover ?? property.imagenes[0];
  return (
    <Link className="property-card" to={`/propiedades/${property.slug}`}>
      <div className="property-media">
        <img
          alt={property.titulo}
          src={image?.url_thumbnail ?? image?.url ?? heroImage}
        />
        <span>{operationLabel(property.tipo_operacion)}</span>
      </div>
      <div className="property-card-body">
        <div>
          <p className="property-location">
            {property.localidad}
            {property.zona ? `, ${property.zona}` : ""}
          </p>
          <h2>{property.titulo}</h2>
        </div>
        <p className="property-price">{formatMoney(property)}</p>
        <dl className="property-facts">
          <div>
            <dt>Dorm.</dt>
            <dd>{property.dormitorios ?? "-"}</dd>
          </div>
          <div>
            <dt>Baños</dt>
            <dd>{property.banios ?? "-"}</dd>
          </div>
          <div>
            <dt>Sup.</dt>
            <dd>{formatArea(property.superficie_total)}</dd>
          </div>
        </dl>
      </div>
    </Link>
  );
}

export function CatalogPage() {
  const [draftFilters, setDraftFilters] = useState(initialFilters);
  const [appliedFilters, setAppliedFilters] = useState(initialFilters);
  const [page, setPage] = useState(initialPage);
  const [offset, setOffset] = useState(0);
  const [state, setState] = useState<LoadState>("loading");

  const currentPage = Math.floor(page.offset / page.limit) + 1;
  const totalPages = Math.max(1, Math.ceil(page.total / page.limit));

  const activeFilters = useMemo(
    () => buildFilters(appliedFilters, offset),
    [appliedFilters, offset],
  );

  useEffect(() => {
    const controller = new AbortController();
    listPublicProperties(activeFilters, controller.signal)
      .then((response) => {
        setPage(response);
        setState("success");
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError")
          return;
        setState("error");
      });
    return () => controller.abort();
  }, [activeFilters]);

  function submitFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setState("loading");
    setOffset(0);
    setAppliedFilters(draftFilters);
  }

  function resetFilters() {
    setState("loading");
    setDraftFilters(initialFilters);
    setAppliedFilters(initialFilters);
    setOffset(0);
  }

  function goToOffset(nextOffset: number) {
    setState("loading");
    setOffset(nextOffset);
  }

  return (
    <section className="catalog-page">
      <div className="page-intro catalog-intro">
        <p className="eyebrow">Catálogo</p>
        <h1>Propiedades para tu próxima etapa.</h1>
        <p>
          Explorá propiedades publicadas con filtros simples y datos preparados
          para tomar una decisión sin perder tiempo.
        </p>
      </div>
      <div className="catalog-content">
        <aside className="catalog-sidebar" aria-label="Filtros del catálogo">
          <form className="catalog-filters" onSubmit={submitFilters}>
            <label>
              Operación
              <select
                value={draftFilters.tipo_operacion}
                onChange={(event) =>
                  setDraftFilters((filters) => ({
                    ...filters,
                    tipo_operacion: event.target
                      .value as DraftFilters["tipo_operacion"],
                  }))
                }
              >
                <option value="">Todas</option>
                <option value="venta">Venta</option>
                <option value="alquiler">Alquiler</option>
                <option value="temporario">Temporario</option>
              </select>
            </label>
            <label>
              Tipo
              <input
                placeholder="Casa, departamento..."
                value={draftFilters.tipo_propiedad}
                onChange={(event) =>
                  setDraftFilters((filters) => ({
                    ...filters,
                    tipo_propiedad: event.target.value,
                  }))
                }
              />
            </label>
            <label>
              Localidad
              <input
                placeholder="Merlo"
                value={draftFilters.localidad}
                onChange={(event) =>
                  setDraftFilters((filters) => ({
                    ...filters,
                    localidad: event.target.value,
                  }))
                }
              />
            </label>
            <div className="filter-row">
              <label>
                Precio mín.
                <input
                  inputMode="numeric"
                  value={draftFilters.precio_min}
                  onChange={(event) =>
                    setDraftFilters((filters) => ({
                      ...filters,
                      precio_min: event.target.value,
                    }))
                  }
                />
              </label>
              <label>
                Precio máx.
                <input
                  inputMode="numeric"
                  value={draftFilters.precio_max}
                  onChange={(event) =>
                    setDraftFilters((filters) => ({
                      ...filters,
                      precio_max: event.target.value,
                    }))
                  }
                />
              </label>
            </div>
            <label>
              Dormitorios desde
              <input
                inputMode="numeric"
                value={draftFilters.dormitorios_min}
                onChange={(event) =>
                  setDraftFilters((filters) => ({
                    ...filters,
                    dormitorios_min: event.target.value,
                  }))
                }
              />
            </label>
            <div className="filter-actions">
              <button className="button button-primary" type="submit">
                Aplicar
              </button>
              <button
                className="button button-secondary"
                type="button"
                onClick={resetFilters}
              >
                Limpiar
              </button>
            </div>
          </form>
        </aside>
        <div className="catalog-results">
          <div className="catalog-toolbar">
            <p>
              {state === "success"
                ? `${page.total} propiedades publicadas`
                : "Buscando propiedades"}
            </p>
            <span>
              Página {currentPage} de {totalPages}
            </span>
          </div>
          {state === "loading" ? (
            <div className="catalog-state" role="status">
              Cargando catálogo...
            </div>
          ) : null}
          {state === "error" ? (
            <div className="catalog-state catalog-state-error" role="alert">
              No pudimos cargar las propiedades. Probá nuevamente en unos
              minutos.
            </div>
          ) : null}
          {state === "success" && page.items.length === 0 ? (
            <div className="catalog-state">
              No hay propiedades publicadas con esos filtros.
            </div>
          ) : null}
          {state === "success" && page.items.length > 0 ? (
            <>
              <div className="property-grid">
                {page.items.map((property) => (
                  <PropertyCard key={property.id} property={property} />
                ))}
              </div>
              <div className="pagination-controls" aria-label="Paginación">
                <button
                  className="button button-secondary"
                  disabled={page.offset === 0}
                  onClick={() => goToOffset(Math.max(0, offset - PAGE_SIZE))}
                  type="button"
                >
                  Anterior
                </button>
                <button
                  className="button button-secondary"
                  disabled={page.offset + page.limit >= page.total}
                  onClick={() => goToOffset(offset + PAGE_SIZE)}
                  type="button"
                >
                  Siguiente
                </button>
              </div>
            </>
          ) : null}
        </div>
      </div>
    </section>
  );
}
