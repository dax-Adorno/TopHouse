import { cleanup, render, screen, waitFor } from "@testing-library/react";
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

const emptyAdminPropertyPage = {
  items: [],
  total: 0,
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

const editedAdminProperty = {
  ...adminPropertyPage.items[0],
  titulo: "Casa luminosa actualizada",
  zona: "Rincón del Este",
};

const adminImages = [
  {
    id: 11,
    propiedad_id: 7,
    nombre_original: "fachada.jpg",
    mime_type: "image/jpeg",
    tamanio_bytes: 120000,
    ancho: 1200,
    alto: 800,
    orden: 0,
    es_portada: true,
    creado_en: "2026-08-21T12:00:00Z",
    url: "https://storage.example/fachada.webp",
    url_thumbnail: "https://storage.example/fachada-thumb.webp",
  },
  {
    id: 12,
    propiedad_id: 7,
    nombre_original: "living.jpg",
    mime_type: "image/jpeg",
    tamanio_bytes: 98000,
    ancho: 1200,
    alto: 800,
    orden: 1,
    es_portada: false,
    creado_en: "2026-08-21T12:30:00Z",
    url: "https://storage.example/living.webp",
    url_thumbnail: "https://storage.example/living-thumb.webp",
  },
];

describe("TopHouse App", () => {
  beforeEach(() => {
    window.history.pushState({}, "", "/");
    vi.unstubAllEnvs();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("muestra la portada y navega al catálogo", async () => {
    const user = userEvent.setup();
    const fetchMock = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(propertyPage),
      }),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent(
      "Tu próximo lugar",
    );
    expect(
      await screen.findByRole("heading", {
        level: 3,
        name: "Casa luminosa en Merlo",
      }),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining(
        "/api/v1/publico/propiedades?destacada=true&limit=3&offset=0",
      ),
      expect.objectContaining({
        headers: { Accept: "application/json" },
      }),
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
    vi.stubEnv("VITE_WHATSAPP_NUMBER", "+54 9 266 400-0000");
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
    expect(
      screen.getByRole("link", {
        name: "Ver Piedra Blanca, Merlo, San Luis en el mapa",
      }),
    ).toHaveAttribute(
      "href",
      expect.stringContaining(
        "query=Piedra%20Blanca%2C%20Merlo%2C%20San%20Luis%2C%20Argentina",
      ),
    );
    const contactLink = screen
      .getAllByRole("link", {
        name: "Contactar por WhatsApp",
      })
      .find((link) =>
        link.getAttribute("href")?.includes("quiero%20consultar"),
      );
    expect(contactLink).toBeDefined();
    expect(contactLink).toHaveAttribute(
      "href",
      expect.stringContaining("https://wa.me/5492664000000?text="),
    );
    expect(contactLink).toHaveAttribute(
      "href",
      expect.stringContaining("Casa%20luminosa%20en%20Merlo"),
    );
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
        url.includes("/api/v1/propiedades/7/imagenes") &&
        options?.method === "POST"
      ) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(adminImages[0]),
        });
      }
      if (
        url.includes("/api/v1/propiedades/7/imagenes/12/portada") &&
        options?.method === "PUT"
      ) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ ...adminImages[1], es_portada: true }),
        });
      }
      if (
        url.includes("/api/v1/propiedades/7/imagenes/orden") &&
        options?.method === "PUT"
      ) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve([adminImages[1], adminImages[0]]),
        });
      }
      if (
        url.includes("/api/v1/propiedades/7/imagenes/11") &&
        options?.method === "DELETE"
      ) {
        return Promise.resolve({ ok: true, status: 204 });
      }
      if (url.includes("/api/v1/propiedades/7/imagenes")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(adminImages),
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
        options?.method === "PATCH"
      ) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(editedAdminProperty),
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

    await user.click(screen.getByRole("button", { name: "Editar datos" }));
    await user.clear(screen.getByLabelText("Título"));
    await user.type(
      screen.getByLabelText("Título"),
      "Casa luminosa actualizada",
    );
    await user.clear(screen.getByLabelText("Zona"));
    await user.type(screen.getByLabelText("Zona"), "Rincón del Este");
    await user.click(screen.getByRole("button", { name: "Guardar datos" }));

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/propiedades/7"),
      expect.objectContaining({
        body: expect.stringContaining("Casa luminosa actualizada"),
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "PATCH",
      }),
    );

    await user.click(screen.getByRole("button", { name: "Imágenes" }));

    expect(await screen.findByText("fachada.jpg")).toBeInTheDocument();
    expect(screen.getByText("living.jpg")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/propiedades/7/imagenes"),
      expect.objectContaining({
        credentials: "include",
      }),
    );

    const file = new File(["contenido"], "living.jpg", { type: "image/jpeg" });
    const fileInput = screen.getByLabelText("Archivo") as HTMLInputElement;
    await user.upload(fileInput, file);
    expect(fileInput.files?.[0]).toBe(file);
    await user.click(screen.getByRole("button", { name: "Subir imagen" }));

    let uploadCall:
      | [input: string | URL | Request, init?: RequestInit | undefined]
      | undefined;
    await waitFor(() => {
      uploadCall = fetchMock.mock.calls.find(
        ([url, options]) =>
          String(url).includes("/api/v1/propiedades/7/imagenes") &&
          (options as RequestInit | undefined)?.method === "POST",
      );
      expect(uploadCall).toBeDefined();
    });
    expect(uploadCall).toBeDefined();
    expect(uploadCall?.[1]).toEqual(
      expect.objectContaining({
        body: expect.any(FormData),
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "POST",
      }),
    );

    await user.click(screen.getAllByRole("button", { name: "Bajar" })[0]);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/propiedades/7/imagenes/orden"),
      expect.objectContaining({
        body: JSON.stringify({ imagen_ids: [12, 11] }),
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "PUT",
      }),
    );

    await user.click(screen.getByRole("button", { name: "Usar como portada" }));

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/propiedades/7/imagenes/12/portada"),
      expect.objectContaining({
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "PUT",
      }),
    );

    await user.click(screen.getAllByRole("button", { name: "Eliminar" })[0]);

    expect(window.confirm).toHaveBeenCalledWith(
      "Eliminar fachada.jpg de TOP-7?",
    );
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/propiedades/7/imagenes/11"),
      expect.objectContaining({
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "DELETE",
      }),
    );

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
          mostrar_ubicacion_exacta: false,
        }),
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "POST",
      }),
    );
  });

  it("permite crear la primera propiedad desde el inventario vacío", async () => {
    const user = userEvent.setup();
    document.cookie = "tophouse_csrf=csrf-prueba";
    const fetchMock = vi.fn((url: string, options?: RequestInit) => {
      if (url.includes("/api/v1/auth/me")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(adminUser),
        });
      }
      if (url.includes("/api/v1/propiedades?limit=100")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(emptyAdminPropertyPage),
        });
      }
      if (url.includes("/api/v1/propiedades") && options?.method === "POST") {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve(createdAdminProperty),
        });
      }
      return Promise.reject(new Error(`Unexpected request: ${url}`));
    });
    vi.stubGlobal("fetch", fetchMock);
    window.history.pushState({}, "", "/admin");

    render(<App />);

    expect(
      await screen.findByText("No hay propiedades cargadas."),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Nueva propiedad" }));
    await user.type(screen.getByLabelText("Código"), "TOP-1");
    await user.type(screen.getByLabelText("Título"), "Casa inicial en Merlo");
    await user.type(
      screen.getByLabelText("Descripción"),
      "Primera propiedad del inventario.",
    );
    await user.type(screen.getByLabelText("Latitud"), "-32.342900");
    await user.click(screen.getByRole("button", { name: "Guardar borrador" }));

    expect(
      await screen.findByText("Ingresá latitud y longitud juntas."),
    ).toBeInTheDocument();
    expect(
      fetchMock.mock.calls.some(
        ([url, options]) =>
          String(url).includes("/api/v1/propiedades") &&
          (options as RequestInit | undefined)?.method === "POST",
      ),
    ).toBe(false);

    await user.type(screen.getByLabelText("Longitud"), "-65.013900");
    await user.click(screen.getByRole("button", { name: "Guardar borrador" }));

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/propiedades"),
      expect.objectContaining({
        body: JSON.stringify({
          codigo: "TOP-1",
          titulo: "Casa inicial en Merlo",
          descripcion: "Primera propiedad del inventario.",
          tipo_operacion: "venta",
          tipo_propiedad: "casa",
          moneda: "USD",
          localidad: "Merlo",
          latitud: "-32.342900",
          longitud: "-65.013900",
          mostrar_ubicacion_exacta: false,
        }),
        credentials: "include",
        headers: expect.objectContaining({
          "X-CSRF-Token": "csrf-prueba",
        }),
        method: "POST",
      }),
    );
    expect(
      await screen.findByText("Propiedad creada como borrador."),
    ).toBeInTheDocument();
  });
});
