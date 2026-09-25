import { useEffect, useState } from "react";
import type { CSSProperties } from "react";
import { Link } from "react-router-dom";
import { FeaturedCarousel } from "../components/FeaturedCarousel";
import { listPublicProperties } from "../lib/api";
import { buildGeneralContactHref } from "../lib/contact";
import type { PublicProperty } from "../types/property";

export function HomePage() {
  const [featured, setFeatured] = useState<PublicProperty[]>([]);
  const [featuredState, setFeaturedState] = useState<
    "loading" | "success" | "error"
  >("loading");

  useEffect(() => {
    const controller = new AbortController();
    listPublicProperties(
      { destacada: true, limit: 3, offset: 0 },
      controller.signal,
    )
      .then((response) => {
        setFeatured(response.items);
        setFeaturedState("success");
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError")
          return;
        setFeaturedState("error");
      });
    return () => controller.abort();
  }, []);

  const heroProperty = featured[0];
  const heroImage =
    heroProperty?.imagenes.find((image) => image.es_portada) ??
    heroProperty?.imagenes[0];
  const heroStyle = heroImage
    ? ({ "--hero-image": `url("${heroImage.url}")` } as CSSProperties)
    : undefined;

  return (
    <>
      <section className="hero-section" style={heroStyle}>
        <div className="hero-copy">
          <h1>Tu próximo lugar empieza con una buena elección.</h1>
          <div className="hero-actions">
            <Link className="button button-primary" to="/propiedades">
              Explorar propiedades
            </Link>
            <a
              className="button button-secondary"
              href={buildGeneralContactHref()}
            >
              Hablar con un asesor
            </a>
          </div>
        </div>
        <div className="hero-visual" aria-label="Identidad de TopHouse">
          <div className="hero-brand-lockup">
            <img
              src="/assets/tophouse-logo.webp"
              alt="TopHouse, Inmobiliaria y Arquitectura"
              width="1774"
              height="887"
            />
          </div>
        </div>
      </section>
      <section className="home-search" aria-label="Buscar propiedades">
        <form action="/propiedades" method="get">
          <label>
            Ubicación
            <select name="localidad" defaultValue="">
              <option value="">Todas las zonas</option>
              <option value="Merlo">Merlo</option>
              <option value="Cortaderas">Cortaderas</option>
              <option value="Carpintería">Carpintería</option>
            </select>
          </label>
          <label>
            Tipo
            <input name="tipo_propiedad" placeholder="Casa, terreno..." />
          </label>
          <label>
            Operación
            <select name="tipo_operacion" defaultValue="">
              <option value="">Venta o alquiler</option>
              <option value="venta">Venta</option>
              <option value="alquiler">Alquiler</option>
              <option value="temporario">Temporario</option>
            </select>
          </label>
          <button className="button button-primary" type="submit">
            Buscar propiedades <span aria-hidden="true">→</span>
          </button>
        </form>
      </section>
      <section className="featured-section" aria-labelledby="featured-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Curaduría local</p>
            <h2 id="featured-title">Oportunidades elegidas en la zona.</h2>
          </div>
          <Link className="button button-secondary" to="/propiedades">
            Ver catálogo
          </Link>
        </div>
        {featuredState === "loading" ? (
          <div className="featured-state" role="status">
            Cargando propiedades destacadas...
          </div>
        ) : null}
        {featuredState === "error" ? (
          <div className="featured-state featured-state-error" role="alert">
            No pudimos cargar las destacadas en este momento.
          </div>
        ) : null}
        {featuredState === "success" && featured.length === 0 ? (
          <div className="featured-state">
            Todavía no hay propiedades destacadas publicadas.
          </div>
        ) : null}
        {featuredState === "success" && featured.length > 0 ? (
          <FeaturedCarousel properties={featured} />
        ) : null}
      </section>
    </>
  );
}
