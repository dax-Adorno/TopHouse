import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import { useSearchParams } from "react-router-dom";
import { PropertyCard } from "../components/PropertyCard";
import { listPublicProperties } from "../lib/api";
import type { PropertyPage, PublicPropertyFilters } from "../types/property";

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

export function CatalogPage() {
  const [searchParams] = useSearchParams();
  const queryFilters = useMemo<DraftFilters>(
    () => ({
      ...initialFilters,
      tipo_operacion: (searchParams.get("tipo_operacion") ??
        "") as DraftFilters["tipo_operacion"],
      tipo_propiedad: searchParams.get("tipo_propiedad") ?? "",
      localidad: searchParams.get("localidad") ?? "",
    }),
    [searchParams],
  );
  const [draftFilters, setDraftFilters] = useState(queryFilters);
  const [appliedFilters, setAppliedFilters] = useState(queryFilters);
  const [page, setPage] = useState(initialPage);
  const [offset, setOffset] = useState(0);
  const [state, setState] = useState<LoadState>("loading");
  const [filterError, setFilterError] = useState<string | null>(null);

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
    if (!isValidPriceRange(draftFilters)) {
      setFilterError("El precio mínimo no puede superar al precio máximo.");
      return;
    }
    setFilterError(null);
    setState("loading");
    setOffset(0);
    setAppliedFilters(draftFilters);
  }

  function resetFilters() {
    setState("loading");
    setFilterError(null);
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
        <h1 className="catalog-title">Catálogo general</h1>
      </div>
      <div className="catalog-content">
        <aside className="catalog-sidebar" aria-label="Filtros del catálogo">
          <div className="catalog-filter-heading">
            <strong>Filtros avanzados</strong>
            <button type="button" onClick={resetFilters}>
              Limpiar
            </button>
          </div>
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
                  min="0"
                  step="1"
                  type="number"
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
                  min="0"
                  step="1"
                  type="number"
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
                min="0"
                step="1"
                type="number"
                value={draftFilters.dormitorios_min}
                onChange={(event) =>
                  setDraftFilters((filters) => ({
                    ...filters,
                    dormitorios_min: event.target.value,
                  }))
                }
              />
            </label>
            {filterError !== null ? (
              <p className="filter-error" role="alert">
                {filterError}
              </p>
            ) : null}
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

function isValidPriceRange(filters: DraftFilters): boolean {
  if (filters.precio_min === "" || filters.precio_max === "") return true;
  return Number(filters.precio_min) <= Number(filters.precio_max);
}
