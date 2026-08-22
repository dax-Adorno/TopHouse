import type { PublicProperty } from "../types/property";

export function approximateLocationLabel(property: PublicProperty): string {
  return [property.zona, property.localidad, "San Luis"]
    .filter(Boolean)
    .join(", ");
}

export function buildApproximateMapHref(property: PublicProperty): string {
  const query = `${approximateLocationLabel(property)}, Argentina`;
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
    query,
  )}`;
}
