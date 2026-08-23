import type {
  AdminProperty,
  AdminPropertyCreate,
  AdminPropertyDetailsUpdate,
  AdminPropertyImage,
  AdminPropertyPage,
  AdminPropertyUpdate,
  PropertyPage,
  PublicProperty,
  PublicPropertyFilters,
} from "../types/property";
import type { AdminUser, LoginCredentials } from "../types/auth";

const API_URL = (
  import.meta.env.VITE_API_URL ?? "http://localhost:8000"
).replace(/\/$/, "");

type RequestOptions = {
  signal?: AbortSignal;
  method?: "DELETE" | "GET" | "POST" | "PATCH" | "PUT";
  body?: unknown;
  credentials?: RequestCredentials;
  csrf?: boolean;
};

function readCookie(name: string): string | null {
  const prefix = `${name}=`;
  return (
    document.cookie
      .split(";")
      .map((cookie) => cookie.trim())
      .find((cookie) => cookie.startsWith(prefix))
      ?.slice(prefix.length) ?? null
  );
}

async function request<T>(
  path: string,
  {
    signal,
    method = "GET",
    body,
    credentials,
    csrf = false,
  }: RequestOptions = {},
): Promise<T> {
  const headers: Record<string, string> = { Accept: "application/json" };
  const isFormData = body instanceof FormData;
  if (body !== undefined && !isFormData)
    headers["Content-Type"] = "application/json";
  if (csrf) {
    const csrfToken = readCookie("tophouse_csrf");
    if (csrfToken !== null) headers["X-CSRF-Token"] = csrfToken;
  }

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body:
      body === undefined ? undefined : isFormData ? body : JSON.stringify(body),
    credentials,
    signal,
  });
  if (!response.ok)
    throw new Error(`La API respondió con estado ${response.status}`);
  if (response.status === 204) return undefined as T;
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
  request<PropertyPage>(`/api/v1/publico/propiedades${buildQuery(filters)}`, {
    signal,
  });
export const getPublicProperty = (slug: string, signal?: AbortSignal) =>
  request<PublicProperty>(
    `/api/v1/publico/propiedades/${encodeURIComponent(slug)}`,
    { signal },
  );

export const login = (credentials: LoginCredentials) =>
  request<AdminUser>("/api/v1/auth/login", {
    method: "POST",
    body: credentials,
    credentials: "include",
  });

export const getCurrentUser = (signal?: AbortSignal) =>
  request<AdminUser>("/api/v1/auth/me", {
    credentials: "include",
    signal,
  });

export const listAdminProperties = (signal?: AbortSignal) =>
  request<AdminPropertyPage>("/api/v1/propiedades?limit=100", {
    credentials: "include",
    signal,
  });

export const listAdminPropertyImages = (
  propertyId: number,
  signal?: AbortSignal,
) =>
  request<AdminPropertyImage[]>(`/api/v1/propiedades/${propertyId}/imagenes`, {
    credentials: "include",
    signal,
  });

export const uploadAdminPropertyImage = (propertyId: number, file: File) => {
  const body = new FormData();
  body.set("archivo", file);
  return request<AdminPropertyImage>(
    `/api/v1/propiedades/${propertyId}/imagenes`,
    {
      method: "POST",
      body,
      credentials: "include",
      csrf: true,
    },
  );
};

export const setAdminPropertyImageCover = (
  propertyId: number,
  imageId: number,
) =>
  request<AdminPropertyImage>(
    `/api/v1/propiedades/${propertyId}/imagenes/${imageId}/portada`,
    {
      method: "PUT",
      credentials: "include",
      csrf: true,
    },
  );

export const deleteAdminPropertyImage = (propertyId: number, imageId: number) =>
  request<void>(`/api/v1/propiedades/${propertyId}/imagenes/${imageId}`, {
    method: "DELETE",
    credentials: "include",
    csrf: true,
  });

export const reorderAdminPropertyImages = (
  propertyId: number,
  imageIds: number[],
) =>
  request<AdminPropertyImage[]>(
    `/api/v1/propiedades/${propertyId}/imagenes/orden`,
    {
      method: "PUT",
      body: { imagen_ids: imageIds },
      credentials: "include",
      csrf: true,
    },
  );

export const createAdminProperty = (property: AdminPropertyCreate) =>
  request<AdminProperty>("/api/v1/propiedades", {
    method: "POST",
    body: property,
    credentials: "include",
    csrf: true,
  });

export const updateAdminPropertyDetails = (
  propertyId: number,
  changes: AdminPropertyDetailsUpdate,
) =>
  request<AdminProperty>(`/api/v1/propiedades/${propertyId}`, {
    method: "PATCH",
    body: changes,
    credentials: "include",
    csrf: true,
  });

export const updateAdminProperty = (
  propertyId: number,
  changes: AdminPropertyUpdate,
) =>
  request<AdminProperty>(`/api/v1/propiedades/${propertyId}/admin`, {
    method: "PATCH",
    body: changes,
    credentials: "include",
    csrf: true,
  });

export const archiveAdminProperty = (propertyId: number) =>
  request<void>(`/api/v1/propiedades/${propertyId}`, {
    method: "DELETE",
    credentials: "include",
    csrf: true,
  });

export const logout = () =>
  request<void>("/api/v1/auth/logout", {
    method: "POST",
    credentials: "include",
    csrf: true,
  });
