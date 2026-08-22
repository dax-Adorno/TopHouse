import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const propertyPage = {
  items: [
    {
      id: 7,
      codigo: "TOP-7",
      slug: "casa-luminosa-merlo",
      titulo: "Casa luminosa en Merlo",
      descripcion: "Casa familiar con patio y ambientes integrados.",
      tipo_operacion: "venta",
      tipo_propiedad: "casa",
      precio: "250000",
      moneda: "USD",
      localidad: "Merlo",
      zona: "Piedra Blanca",
      dormitorios: 3,
      banios: 2,
      superficie_cubierta: "180",
      superficie_total: "420",
      estado: "publicada",
      destacada: true,
      imagenes: [
        {
          id: 3,
          url: "https://storage.example/fachada.webp",
          url_thumbnail: "https://storage.example/fachada-thumb.webp",
          ancho: 1200,
          alto: 800,
          orden: 0,
          es_portada: true,
        },
      ],
      creado_en: "2026-08-21T12:00:00Z",
      actualizado_en: "2026-08-21T12:00:00Z",
    },
  ],
  total: 1,
  offset: 0,
  limit: 9,
};

const adminUser = {
  id: 1,
  email: "admin@tophouse.com",
  nombre: "Admin TopHouse",
  rol: "administrador",
  activo: true,
  ultimo_acceso_en: null,
  creado_en: "2026-08-21T12:00:00Z",
  actualizado_en: "2026-08-21T12:00:00Z",
};

const adminPropertyPage = {
  items: [
    {
      ...propertyPage.items[0],
      direccion: "Piedra Blanca",
      latitud: "-32.342900",
      longitud: "-65.013900",
      mostrar_ubicacion_exacta: false,
    },
  ],
  total: 1,
  offset: 0,
  limit: 100,
};

const createdAdminProperty = {
  ...adminPropertyPage.items[0],
  id: 8,
  codigo: "TOP-8",
  slug: "casa-en-merlo",
  titulo: "Casa en Merlo",
  descripcion: "Casa nueva con patio.",
  localidad: "Merlo",
  zona: "Centro",
  estado: "borrador",
  destacada: false,
};

const updatedAdminProperty = {
  ...adminPropertyPage.items[0],
  estado: "pausada",
  destacada: false,
};

describe("TopHouse App", () => {
  beforeEach(() => {
    window.history.pushState({}, "", "/");
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("muestra la portada y navega al catálogo", async () => {
    const user = userEvent.setup();
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(propertyPage),
        }),
      ),
    );

    render(<App />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Tu próximo lugar",
    );
    await user.click(
      screen.getByRole("link", { name: "Explorar propiedades" }),
    );
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Propiedades para tu próxima etapa",
    );
  });

  it("lista propiedades públicas y aplica filtros", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(propertyPage),
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    window.history.pushState({}, "", "/propiedades");

    render(<App />);

    expect(
      await screen.findByText("Casa luminosa en Merlo"),
    ).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Operación"), "venta");
    await user.type(screen.getByLabelText("Localidad"), "Merlo");
    await user.click(screen.getByRole("button", { name: "Aplicar" }));

    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining(
        "/api/v1/publico/propiedades?tipo_operacion=venta&localidad=Merlo",
      ),
      expect.objectContaining({
        headers: { Accept: "application/json" },
      }),
    );
  });

  it("abre el detalle público desde una tarjeta del catálogo", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn((url: string) =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve(
            url.includes("/api/v1/publico/propiedades/casa-luminosa-merlo")
              ? propertyPage.items[0]
              : propertyPage,
          ),
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    window.history.pushState({}, "", "/propiedades");

    render(<App />);

    await user.click(
      await screen.findByRole("link", { name: /Casa luminosa en Merlo/i }),
    );

    expect(
      await screen.findByRole("heading", { level: 1, name: /Casa luminosa/i }),
    ).toBeInTheDocument();
    expect(screen.getByText("Descripción")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining(
        "/api/v1/publico/propiedades/casa-luminosa-merlo",
      ),
      expect.objectContaining({
        headers: { Accept: "application/json" },
      }),
    );
  });

  it("permite iniciar sesión administrativa y crear un borrador", async () => {
    const user = userEvent.setup();
    document.cookie = "tophouse_csrf=csrf-prueba";
    vi.stubGlobal(
      "confirm",
      vi.fn(() => true),
    );
    const fetchMock = vi.fn((url: string, options?: RequestInit) => {
      if (url.includes("/api/v1/auth/me")) {
        return Promise.resolve({ ok: false, status: 401 });
      }
      if (url.includes("/api/v1/auth/login")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(adminUser),
        });
      }
      if (
        url.includes("/api/v1/propiedades/7/admin") &&
        options?.method === "PATCH"
      ) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(updatedAdminProperty),
        });
      }
      if (
        url.includes("/api/v1/propiedades/7") &&
        options?.method === "DELETE"
      ) {
        return Promise.resolve({ ok: true, status: 204 });
      }
      if (url.includes("/api/v1/propiedades") && options?.method === "POST") {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(createdAdminProperty),
        });
      }
      if (url.includes("/api/v1/propiedades?limit=100")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(adminPropertyPage),
        });
      }
      return Promise.reject(new Error(`Unexpected request: ${url}`));
    });
    vi.stubGlobal("fetch", fetchMock);
    window.history.pushState({}, "", "/admin");

    render(<App />);

    await user.type(await screen.findByLabelText("Email"), adminUser.email);
    await user.type(screen.getByLabelText("Contraseña"), "clave-segura");
    await user.click(screen.getByRole("button", { name: "Ingresar" }));

    expect(
      await screen.findByRole("heading", { name: "Panel de TopHouse" }),
    ).toBeInTheDocument();
    expect(
      await screen.findByText("Casa luminosa en Merlo"),
    ).toBeInTheDocument();
    expect(screen.getByText("TOP-7")).toBeInTheDocument();
    expect(screen.getByText("Publicada")).toBeInTheDocument();

    await user.selectOptions(
      screen.getByLabelText("Estado de TOP-7"),
      "pausada",
    );
    await user.click(screen.getByLabelText("Destacada TOP-7"));
    await user.click(screen.getByRole("button", { name: "Guardar" }));

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/propiedades/7/admin"),
      expect.objectContaining({
        body: JSON.stringify({ estado: "pausada", destacada: false }),
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "PATCH",
      }),
    );

    await user.click(screen.getByRole("button", { name: "Archivar" }));

    expect(window.confirm).toHaveBeenCalledWith(
      "Archivar TOP-7 y quitarla del catálogo público?",
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/propiedades/7"),
      expect.objectContaining({
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "DELETE",
      }),
    );

    await user.click(screen.getByRole("button", { name: "Nueva propiedad" }));
    await user.type(screen.getByLabelText("Código"), "TOP-8");
    await user.type(screen.getByLabelText("Título"), "Casa en Merlo");
    await user.type(
      screen.getByLabelText("Descripción"),
      "Casa nueva con patio.",
    );
    await user.click(screen.getByRole("button", { name: "Guardar borrador" }));

    expect(
      await screen.findByText("Propiedad creada como borrador."),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining("/api/v1/propiedades?limit=100"),
      expect.objectContaining({
        credentials: "include",
      }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/auth/login"),
      expect.objectContaining({
        body: JSON.stringify({
          email: adminUser.email,
          contrasena: "clave-segura",
        }),
        credentials: "include",
        method: "POST",
      }),
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/propiedades"),
      expect.objectContaining({
        body: JSON.stringify({
          codigo: "TOP-8",
          titulo: "Casa en Merlo",
          descripcion: "Casa nueva con patio.",
          tipo_operacion: "venta",
          tipo_propiedad: "casa",
          moneda: "USD",
          localidad: "Merlo",
        }),
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "POST",
      }),
    );
  });
});
