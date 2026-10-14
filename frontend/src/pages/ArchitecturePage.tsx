import { useState } from "react";
import { Link } from "react-router-dom";
import "../styles/architecture.css";

const projects = [
  {
    id: "mirador",
    name: "Edificio Mirador",
    category: "Residencial · 4 plantas",
    status: "Realizada",
    description:
      "Viviendas en altura con espacios luminosos y una distribución que conecta cada ambiente con el exterior.",
    area: "960 m²",
    program: "8 departamentos · 4 plantas",
    system: "Estructura de hormigón armado y cerramientos de mampostería.",
    finish:
      "Revoque exterior, carpinterías de aluminio y pisos de porcelanato.",
    rooms: ["Departamento A", "Departamento B", "Escalera", "Hall común"],
    note: "Planta tipo · dos unidades por nivel",
    kind: "building",
  },
  {
    id: "sierras",
    name: "Chalet Las Sierras",
    category: "Vivienda · Fin de semana",
    status: "Realizada",
    description:
      "Un refugio para disfrutar el fin de semana, con galería, jardín y espacios compartidos abiertos al paisaje.",
    area: "145 m²",
    program: "2 dormitorios · galería · 1 planta",
    system:
      "Mampostería portante y cubierta inclinada con estructura de madera.",
    finish: "Piedra en fachada, cielorrasos de madera y pisos cerámicos.",
    rooms: ["Dormitorio 1", "Dormitorio 2", "Estar / cocina", "Galería"],
    note: "Planta general · vivienda y galería",
    kind: "chalet",
  },
  {
    id: "paseo",
    name: "Paseo Comercial",
    category: "Comercial · 6 locales para alquiler",
    status: "Próxima",
    description:
      "Seis locales independientes con frentes vidriados y un paseo peatonal común, pensados para distintas actividades comerciales.",
    area: "360 m²",
    program: "6 locales · acceso independiente",
    system: "Estructura de hormigón armado y cubierta metálica aislada.",
    finish:
      "Frentes vidriados, pisos de alto tránsito y previsión de cartelería.",
    rooms: [
      "Local 01",
      "Local 02",
      "Local 03",
      "Local 04",
      "Local 05",
      "Local 06",
    ],
    note: "Planta general · seis unidades comerciales",
    kind: "commercial",
  },
] as const;

function ProjectDrawing({
  project,
  plan = false,
}: {
  project: (typeof projects)[number];
  plan?: boolean;
}) {
  return (
    <svg
      viewBox="0 0 600 300"
      role="img"
      aria-label={`${plan ? "Plano esquemático" : "Elevación conceptual"} de ${project.name}`}
      className="architecture-drawing"
    >
      <defs>
        <pattern
          id={`grid-${project.id}-${plan}`}
          width="30"
          height="30"
          patternUnits="userSpaceOnUse"
        >
          <path
            d="M 30 0 L 0 0 0 30"
            fill="none"
            stroke="currentColor"
            strokeWidth="0.5"
            opacity="0.12"
          />
        </pattern>
      </defs>
      <rect
        width="600"
        height="300"
        fill={`url(#grid-${project.id}-${plan})`}
      />
      <g fill="none" stroke="currentColor" strokeWidth="2">
        {plan ? (
          <>
            <rect x="60" y="55" width="480" height="190" strokeWidth="4" />
            {project.rooms.map((room, index) => {
              const commercial = project.kind === "commercial";
              const width = commercial ? 80 : 240;
              const height = commercial ? 190 : 95;
              const x = 60 + (commercial ? index * 80 : (index % 2) * 240);
              const y = commercial ? 55 : 55 + Math.floor(index / 2) * 95;
              return (
                <g key={room}>
                  <rect x={x} y={y} width={width} height={height} />
                  <text
                    x={x + width / 2}
                    y={y + height / 2}
                    textAnchor="middle"
                    fill="currentColor"
                    stroke="none"
                    fontSize={commercial ? 12 : 15}
                  >
                    {room}
                  </text>
                  <path
                    d={`M ${x + 15} ${y + height} a 24 24 0 0 1 24 -24`}
                    strokeWidth="1"
                  />
                </g>
              );
            })}
            <path d="M60 265H540M60 258V272M540 258V272" strokeWidth="1" />
            <text
              x="300"
              y="287"
              textAnchor="middle"
              stroke="none"
              fill="currentColor"
              fontSize="11"
            >
              DISTRIBUCIÓN CONCEPTUAL · SIN ESCALA
            </text>
          </>
        ) : project.kind === "building" ? (
          <>
            <rect x="160" y="40" width="280" height="220" strokeWidth="3" />
            {[0, 1, 2, 3].map((floor) => (
              <g key={floor}>
                <path d={`M150 ${95 + floor * 55}H450`} />
                {[0, 1, 2].map((window) => (
                  <rect
                    key={window}
                    x={185 + window * 80}
                    y={55 + floor * 55}
                    width="50"
                    height="28"
                  />
                ))}
              </g>
            ))}
          </>
        ) : project.kind === "chalet" ? (
          <>
            <path
              d="M95 145L245 55L395 145M125 130V255H465V145H395M395 145L445 110L495 145"
              strokeWidth="3"
            />
            <rect x="170" y="160" width="65" height="55" />
            <rect x="265" y="160" width="55" height="95" />
            <path d="M395 145V255M445 145V255" />
          </>
        ) : (
          <>
            <rect x="60" y="110" width="480" height="145" strokeWidth="3" />
            <path d="M50 110H550M60 145H540" />
            {[0, 1, 2, 3, 4, 5].map((unit) => (
              <g key={unit}>
                <rect x={70 + unit * 80} y="155" width="60" height="100" />
                <path d={`M${100 + unit * 80} 155V255`} />
                <text
                  x={100 + unit * 80}
                  y="133"
                  textAnchor="middle"
                  stroke="none"
                  fill="currentColor"
                  fontSize="12"
                >
                  0{unit + 1}
                </text>
              </g>
            ))}
          </>
        )}
        {!plan && <path d="M40 260H560" strokeWidth="1" />}
      </g>
    </svg>
  );
}

export function ArchitecturePage() {
  const [filter, setFilter] = useState("Todos los proyectos");
  const visible = projects.filter(
    (project) =>
      filter === "Todos los proyectos" ||
      (filter === "Obras realizadas"
        ? project.status === "Realizada"
        : project.status === "Próxima"),
  );
  return (
    <div className="architecture-page">
      <section
        className="architecture-hero"
        aria-labelledby="architecture-title"
      >
        <div>
          <p className="eyebrow">TopHouse · Inmobiliaria & arquitectura</p>
          <h1 id="architecture-title">Arquitectura</h1>
          <p className="architecture-intro">
            Del primer plano al espacio que imaginás.
          </p>
          <p>
            Conocé nuestros proyectos, sus detalles de construcción y las obras
            que dan forma a nuevas maneras de habitar.
          </p>
          <a className="button button-primary" href="#architecture-projects">
            Explorar proyectos ↓
          </a>
        </div>
        <div className="architecture-hero-art">
          <ProjectDrawing project={projects[0]} />
          <span>Diseñar. Construir. Habitar.</span>
        </div>
      </section>
      <section
        className="architecture-portfolio"
        id="architecture-projects"
        aria-labelledby="portfolio-title"
      >
        <p className="eyebrow">Proyectos y obras</p>
        <h2 id="portfolio-title">Ideas que toman forma.</h2>
        <p className="architecture-demo-note">
          Portfolio de muestra: los tres proyectos, sus estados y sus datos son
          ficticios. Los dibujos son esquemas conceptuales, no planos aptos para
          construcción.
        </p>
        <div
          className="architecture-filters"
          role="group"
          aria-label="Filtrar proyectos por estado"
        >
          {["Todos los proyectos", "Obras realizadas", "Próximas obras"].map(
            (label) => (
              <button
                key={label}
                type="button"
                aria-pressed={filter === label}
                onClick={() => setFilter(label)}
              >
                {label}
              </button>
            ),
          )}
        </div>
        <p className="sr-only" role="status">
          {visible.length} proyectos visibles
        </p>
        <div className="architecture-grid">
          {visible.map((project) => (
            <article className="architecture-card" key={project.id}>
              <div className="architecture-card-art">
                <span className="architecture-status">
                  {project.status === "Realizada"
                    ? "Obra realizada"
                    : "Próxima obra"}
                </span>
                <ProjectDrawing project={project} />
              </div>
              <div className="architecture-card-body">
                <p className="eyebrow">{project.category}</p>
                <h3>{project.name}</h3>
                <p>{project.description}</p>
                <dl className="architecture-facts">
                  <div>
                    <dt>Superficie estimada</dt>
                    <dd>{project.area}</dd>
                  </div>
                  <div>
                    <dt>Programa</dt>
                    <dd>{project.program}</dd>
                  </div>
                </dl>
                <details>
                  <summary>
                    Ver planos y detalles <span aria-hidden="true">＋</span>
                  </summary>
                  <div className="architecture-plan">
                    <ProjectDrawing project={project} plan />
                    <p>{project.note}</p>
                  </div>
                  <dl className="architecture-specs">
                    <div>
                      <dt>Sistema constructivo</dt>
                      <dd>{project.system}</dd>
                    </div>
                    <div>
                      <dt>Terminaciones propuestas</dt>
                      <dd>{project.finish}</dd>
                    </div>
                  </dl>
                  <p className="architecture-plan-note">
                    Plano ilustrativo sin escala. Datos de ejemplo sujetos a
                    definición.
                  </p>
                </details>
              </div>
            </article>
          ))}
        </div>
      </section>
      <section className="architecture-contact">
        <div>
          <p className="eyebrow">Tu próximo proyecto</p>
          <h2>Construyamos tu idea.</h2>
          <p>
            Conversá con nuestro equipo sobre tu vivienda, edificio o espacio
            comercial.
          </p>
        </div>
        <Link className="button button-primary" to="/contacto">
          Consultar por arquitectura →
        </Link>
      </section>
    </div>
  );
}
