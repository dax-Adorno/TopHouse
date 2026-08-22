import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import heroImage from "../assets/hero.png";
import { listPublicProperties } from "../lib/api";
import { buildGeneralContactHref } from "../lib/contact";
import { formatMoney, operationLabel } from "../lib/propertyFormat";
import type { PublicProperty } from "../types/property";

const valores = [
  [
    "Selección cuidada",
    "Cada propiedad se presenta con información clara y verificada.",
  ],
  [
    "Acompañamiento real",
    "Te acompañamos desde la primera consulta hasta la decisión final.",
  ],
  [
    "Visión local",
    "Conocemos los barrios, ritmos y oportunidades de Merlo y San Luis.",
  ],
];

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

  return (
    <>
      <section className="hero-section">
        <div className="hero-copy">
          <p className="eyebrow">Inmobiliaria en Merlo, San Luis</p>
          <h1>Tu próximo lugar empieza con una buena elección.</h1>
          <p className="hero-lead">
            Descubrí propiedades para vivir, invertir o empezar una nueva etapa,
            con información transparente y atención personalizada.
          </p>
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
        <div className="hero-visual" aria-label="Arquitectura contemporánea">
          <div className="sun" />
          <div className="building building-back" />
          <div className="building building-front">
            <span />
            <span />
            <span />
          </div>
          <p>
            <strong>Selección TopHouse</strong>
            <br />
            Espacios con intención
          </p>
        </div>
      </section>
      <section className="featured-section" aria-labelledby="featured-title">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Propiedades destacadas</p>
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
          <div className="featured-grid">
            {featured.map((property) => {
              const cover =
                property.imagenes.find((image) => image.es_portada) ??
                property.imagenes[0];
              return (
                <Link
                  className="featured-card"
                  key={property.id}
                  to={`/propiedades/${property.slug}`}
                >
                  <img
                    alt={property.titulo}
                    src={cover?.url_thumbnail ?? cover?.url ?? heroImage}
                  />
                  <span>{operationLabel(property.tipo_operacion)}</span>
                  <div>
                    <p>
                      {property.localidad}
                      {property.zona ? `, ${property.zona}` : ""}
                    </p>
                    <h3>{property.titulo}</h3>
                    <strong>{formatMoney(property)}</strong>
                  </div>
                </Link>
              );
            })}
          </div>
        ) : null}
      </section>
      <section className="values-section" aria-labelledby="values-title">
        <div>
          <p className="eyebrow">Nuestra forma de trabajar</p>
          <h2 id="values-title">Menos ruido. Mejores decisiones.</h2>
        </div>
        <div className="value-grid">
          {valores.map(([titulo, descripcion], index) => (
            <article key={titulo}>
              <span>0{index + 1}</span>
              <h3>{titulo}</h3>
              <p>{descripcion}</p>
            </article>
          ))}
        </div>
      </section>
    </>
  );
}
