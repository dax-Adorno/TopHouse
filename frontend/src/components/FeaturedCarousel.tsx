import {
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
} from "react";
import { Link } from "react-router-dom";
import heroImage from "../assets/hero.png";
import { formatMoney, operationLabel } from "../lib/propertyFormat";
import type { PublicProperty } from "../types/property";

type FeaturedCarouselProps = {
  properties: PublicProperty[];
};

export function FeaturedCarousel({ properties }: FeaturedCarouselProps) {
  const [activeIndex, setActiveIndex] = useState(0);
  const pointerStart = useRef<number | null>(null);
  const dragged = useRef(false);
  const lastIndex = properties.length - 1;

  const goTo = (index: number) => {
    setActiveIndex(Math.max(0, Math.min(index, lastIndex)));
  };

  const handlePointerDown = (event: ReactPointerEvent<HTMLDivElement>) => {
    pointerStart.current = event.clientX;
    dragged.current = false;
    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (pointerStart.current === null) return;
    if (Math.abs(event.clientX - pointerStart.current) > 8)
      dragged.current = true;
  };

  const handlePointerUp = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (pointerStart.current === null) return;
    const distance = event.clientX - pointerStart.current;
    pointerStart.current = null;
    if (Math.abs(distance) < 45) return;
    goTo(activeIndex + (distance < 0 ? 1 : -1));
  };

  return (
    <div
      className="featured-carousel"
      role="region"
      aria-roledescription="carrusel"
      aria-label="Propiedades destacadas"
      tabIndex={0}
      onKeyDown={(event) => {
        if (event.key === "ArrowLeft") goTo(activeIndex - 1);
        if (event.key === "ArrowRight") goTo(activeIndex + 1);
      }}
    >
      <div
        className="featured-carousel-stage"
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerCancel={() => {
          pointerStart.current = null;
        }}
      >
        {properties.map((property, index) => {
          const cover =
            property.imagenes.find((image) => image.es_portada) ??
            property.imagenes[0];
          const offset = index - activeIndex;
          const isActive = offset === 0;
          return (
            <Link
              className="featured-card"
              data-active={isActive}
              aria-hidden={!isActive}
              tabIndex={isActive ? 0 : -1}
              key={property.id}
              to={`/propiedades/${property.slug}`}
              style={{
                opacity: Math.abs(offset) > 1 ? 0 : isActive ? 1 : 0.52,
                pointerEvents: Math.abs(offset) > 1 ? "none" : "auto",
                transform: `translateX(${offset * 62}%) rotateY(${offset * -18}deg) scale(${isActive ? 1 : 0.82})`,
                zIndex: properties.length - Math.abs(offset),
              }}
              onClick={(event) => {
                if (dragged.current) event.preventDefault();
                else if (!isActive) {
                  event.preventDefault();
                  goTo(index);
                }
              }}
            >
              <img
                alt={property.titulo}
                src={cover?.url_thumbnail ?? cover?.url ?? heroImage}
                loading={isActive ? "eager" : "lazy"}
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

      {properties.length > 1 ? (
        <div className="featured-carousel-navigation">
          <button
            type="button"
            aria-label="Propiedad destacada anterior"
            disabled={activeIndex === 0}
            onClick={() => goTo(activeIndex - 1)}
          >
            <span aria-hidden="true">←</span>
          </button>
          <div className="featured-carousel-dots" aria-label="Elegir propiedad">
            {properties.map((property, index) => (
              <button
                type="button"
                key={property.id}
                aria-label={`Mostrar ${property.titulo}`}
                aria-current={index === activeIndex ? "true" : undefined}
                onClick={() => goTo(index)}
              />
            ))}
          </div>
          <p aria-live="polite">
            <strong>{String(activeIndex + 1).padStart(2, "0")}</strong>
            <span> / {String(properties.length).padStart(2, "0")}</span>
          </p>
          <button
            type="button"
            aria-label="Siguiente propiedad destacada"
            disabled={activeIndex === lastIndex}
            onClick={() => goTo(activeIndex + 1)}
          >
            <span aria-hidden="true">→</span>
          </button>
        </div>
      ) : null}
    </div>
  );
}
