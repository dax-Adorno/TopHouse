import type {
  PropertyPage,
  PublicProperty,
  PublicPropertyFilters,
} from "../types/property";

const API_URL = (
  import.meta.env.VITE_API_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { Accept: "application/json" },
    signal,
  });
  if (!response.ok)
    throw new Error(`La API respondió con estado ${response.status}`);
  return response.json() as Promise<T>;
}

function buildQuery(filters: PublicPropertyFilters): string {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") params.set(key, String(value));
  });
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const listPublicProperties = (
  filters: PublicPropertyFilters = {},
  signal?: AbortSignal,
) =>
  request<PropertyPage>(
    `/api/v1/publico/propiedades${buildQuery(filters)}`,
    signal,
  );
export const getPublicProperty = (slug: string, signal?: AbortSignal) =>
  request<PublicProperty>(
    `/api/v1/publico/propiedades/${encodeURIComponent(slug)}`,
    signal,
  );
