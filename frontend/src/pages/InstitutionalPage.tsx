import { Link } from "react-router-dom";
import { buildGeneralContactHref, contactActionLabel } from "../lib/contact";

const sections = {
  nosotros: {
    title: "Nosotros",
    description: "TopHouse. Inmobiliaria y arquitectura en Merlo, San Luis.",
    pending:
      "Próximamente compartiremos nuestra historia y el equipo detrás de TopHouse.",
  },
  servicios: {
    title: "Servicios",
    description: "Inmobiliaria y arquitectura, en un mismo lugar.",
    pending:
      "Estamos preparando el detalle de nuestros servicios. Mientras tanto, podés consultar directamente con TopHouse.",
  },
  proyectos: {
    title: "Proyectos",
    description: "Un espacio para conocer los proyectos de TopHouse.",
    pending:
      "Próximamente encontrarás aquí los proyectos, sus imágenes y sus detalles.",
  },
  obras: {
    title: "Obras",
    description: "Un espacio para conocer nuestras obras.",
    pending: "Próximamente compartiremos las obras y sus avances.",
  },
  prensa: {
    title: "Prensa",
    description: "TopHouse en los medios.",
    pending: "Todavía no hay notas de prensa publicadas en esta sección.",
  },
  blog: {
    title: "Blog",
    description: "Novedades de TopHouse.",
    pending:
      "Todavía no hay artículos publicados. Próximamente sumaremos contenido.",
  },
};

export type InstitutionalSection = keyof typeof sections;

export function InstitutionalPage({
  section,
}: {
  section: InstitutionalSection;
}) {
  const content = sections[section];
  return (
    <section
      className="institutional-page"
      aria-labelledby="institutional-title"
    >
      <div className="institutional-heading">
        <p className="eyebrow">TopHouse · Merlo, San Luis</p>
        <h1 id="institutional-title">{content.title}</h1>
        <p>{content.description}</p>
      </div>
      <div className="institutional-panel">
        <span className="publication-status">Próximamente</span>
        <p>{content.pending}</p>
        <div className="institutional-actions">
          <Link className="button button-primary" to="/contacto">
            Consultar con TopHouse
          </Link>
          <Link className="button button-secondary" to="/propiedades">
            Ver propiedades
          </Link>
        </div>
      </div>
    </section>
  );
}

export function ContactPage() {
  return (
    <section className="institutional-page" aria-labelledby="contact-title">
      <div className="institutional-heading">
        <p className="eyebrow">TopHouse · Merlo, San Luis</p>
        <h1 id="contact-title">Contacto</h1>
        <p>Hablemos de tu próxima propiedad.</p>
      </div>
      <div className="contact-grid">
        <article className="institutional-panel">
          <h2>Contactá con TopHouse</h2>
          <p>
            Consultanos por las propiedades y por nuestros servicios de
            inmobiliaria y arquitectura.
          </p>
          <a className="button button-primary" href={buildGeneralContactHref()}>
            {contactActionLabel()}
          </a>
        </article>
        <aside className="institutional-panel" aria-label="Datos de contacto">
          <dl className="contact-details">
            <div>
              <dt>Teléfono</dt>
              <dd>
                <a href="tel:+5492664320295">+54 9 2664 32-0295</a>
              </dd>
            </div>
            <div>
              <dt>Ubicación</dt>
              <dd>Merlo, San Luis</dd>
            </div>
          </dl>
          <p>
            Si tu consulta es por una propiedad, usá el botón de contacto de su
            ficha para incluir el enlace de la publicación.
          </p>
          <Link className="button button-secondary" to="/propiedades">
            Ir al catálogo
          </Link>
        </aside>
      </div>
    </section>
  );
}
