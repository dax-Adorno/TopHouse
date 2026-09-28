import { Link } from "react-router-dom";
import { PropertyPhoto } from "./PropertyPhoto";
import {
  buildPropertyContactHref,
  propertyContactActionLabel,
} from "../lib/contact";
import { formatArea, formatMoney, operationLabel } from "../lib/propertyFormat";
import type { PublicProperty } from "../types/property";

export function PropertyCard({ property }: { property: PublicProperty }) {
  const cover = property.imagenes.find((image) => image.es_portada);
  const image = cover ?? property.imagenes[0];
  return (
    <article className="property-card">
      <Link
        className="property-card-details"
        to={`/propiedades/${property.slug}`}
      >
        <div className="property-media">
          <PropertyPhoto image={image} alt={property.titulo} thumbnail />
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
      <div className="property-card-actions">
        <a
          className="button button-primary"
          href={buildPropertyContactHref(property)}
          target="_blank"
          rel="noreferrer"
        >
          {propertyContactActionLabel()}
        </a>
      </div>
    </article>
  );
}
