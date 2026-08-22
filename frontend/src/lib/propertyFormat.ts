import type { AdminProperty, PublicProperty } from "../types/property";

type PricedProperty = Pick<PublicProperty | AdminProperty, "moneda" | "precio">;

export function formatMoney(property: PricedProperty): string {
  if (property.precio === null) return "Consultar";
  const value = Number(property.precio);
  const currency = property.moneda ?? "USD";
  if (!Number.isFinite(value)) return `${currency} ${property.precio}`;
  return new Intl.NumberFormat("es-AR", {
    style: "currency",
    currency,
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatArea(value: string | null): string {
  if (value === null) return "-";
  const numeric = Number(value);
  if (!Number.isFinite(numeric)) return `${value} m²`;
  return `${numeric.toLocaleString("es-AR")} m²`;
}

export function operationLabel(
  operation: PublicProperty["tipo_operacion"] | AdminProperty["tipo_operacion"],
): string {
  const labels = {
    venta: "Venta",
    alquiler: "Alquiler",
    temporario: "Temporario",
  };
  return labels[operation];
}
