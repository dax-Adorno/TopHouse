import { Link } from "react-router-dom";

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
    "Conocemos los barrios, ritmos y oportunidades del mercado paraguayo.",
  ],
];

export function HomePage() {
  return (
    <>
      <section className="hero-section">
        <div className="hero-copy">
          <p className="eyebrow">Inmobiliaria en Paraguay</p>
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
              href="mailto:contacto@tophouse.com"
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
