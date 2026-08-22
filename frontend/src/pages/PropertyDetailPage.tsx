import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import heroImage from "../assets/hero.png";
import { getPublicProperty } from "../lib/api";
import { buildPropertyContactHref, contactActionLabel } from "../lib/contact";
import { formatArea, formatMoney, operationLabel } from "../lib/propertyFormat";
import type { PropertyImage, PublicProperty } from "../types/property";

type LoadState = "loading" | "success" | "error";

function getGallery(property: PublicProperty): PropertyImage[] {
  return property.imagenes.length > 0
    ? property.imagenes
    : [
        {
          id: 0,
          url: heroImage,
          url_thumbnail: heroImage,
          ancho: 1200,
          alto: 800,
          orden: 0,
          es_portada: true,
        },
      ];
}

export function PropertyDetailPage() {
  const { slug } = useParams();
  const [property, setProperty] = useState<PublicProperty | null>(null);
  const [state, setState] = useState<LoadState>("loading");
  const [selectedImage, setSelectedImage] = useState(0);

  useEffect(() => {
    if (!slug) return;
    const controller = new AbortController();
    getPublicProperty(slug, controller.signal)
      .then((response) => {
        setProperty(response);
        setSelectedImage(0);
        setState("success");
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError")
          return;
        setState("error");
      });
    return () => controller.abort();
  }, [slug]);

  const gallery = useMemo(
    () => (property ? getGallery(property) : []),
    [property],
  );
  const hero = gallery[selectedImage] ?? gallery[0];

  if (state === "loading") {
    return (
      <section className="detail-state" role="status">
        Cargando propiedad...
      </section>
    );
  }

  if (!slug || state === "error" || property === null) {
    return (
      <section className="detail-state detail-state-error" role="alert">
        No pudimos cargar esta propiedad.
        <Link className="button button-secondary" to="/propiedades">
          Volver al catálogo
        </Link>
      </section>
    );
  }

  return (
    <section className="property-detail">
      <div className="detail-topbar">
        <Link to="/propiedades">Volver al catálogo</Link>
        <span>{operationLabel(property.tipo_operacion)}</span>
      </div>
      <div className="detail-hero">
        <div className="detail-copy">
          <p className="eyebrow">
            {property.localidad}
            {property.zona ? `, ${property.zona}` : ""}
          </p>
          <h1>{property.titulo}</h1>
          <p className="detail-price">{formatMoney(property)}</p>
        </div>
        <a
          className="button button-primary"
          href={buildPropertyContactHref(property)}
        >
          {contactActionLabel()}
        </a>
      </div>
      <div className="detail-gallery">
        <div className="detail-main-image">
          <img alt={property.titulo} src={hero?.url ?? heroImage} />
        </div>
        {gallery.length > 1 ? (
          <div className="detail-thumbs" aria-label="Galería de imágenes">
            {gallery.map((image, index) => (
              <button
                aria-label={`Ver imagen ${index + 1}`}
                aria-pressed={selectedImage === index}
                key={image.id}
                onClick={() => setSelectedImage(index)}
                type="button"
              >
                <img alt="" src={image.url_thumbnail} />
              </button>
            ))}
          </div>
        ) : null}
      </div>
      <div className="detail-content">
        <article className="detail-description">
          <h2>Descripción</h2>
          <p>{property.descripcion}</p>
        </article>
        <aside className="detail-summary" aria-label="Resumen de la propiedad">
          <dl>
            <div>
              <dt>Tipo</dt>
              <dd>{property.tipo_propiedad}</dd>
            </div>
            <div>
              <dt>Dormitorios</dt>
              <dd>{property.dormitorios ?? "-"}</dd>
            </div>
            <div>
              <dt>Baños</dt>
              <dd>{property.banios ?? "-"}</dd>
            </div>
            <div>
              <dt>Sup. cubierta</dt>
              <dd>{formatArea(property.superficie_cubierta)}</dd>
            </div>
            <div>
              <dt>Sup. total</dt>
              <dd>{formatArea(property.superficie_total)}</dd>
            </div>
            <div>
              <dt>Ubicación</dt>
              <dd>
                {property.localidad}
                {property.zona ? `, ${property.zona}` : ""}
              </dd>
            </div>
          </dl>
        </aside>
      </div>
      <div className="detail-location">
        <h2>Ubicación aproximada</h2>
        <p>
          La ubicación pública muestra zona y localidad. La dirección exacta se
          comparte durante la consulta comercial.
        </p>
      </div>
    </section>
  );
}
