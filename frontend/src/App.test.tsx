import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

const propertyPage = {
  items: [
    {
      id: 7,
      codigo: "TOP-7",
      slug: "casa-luminosa",
      titulo: "Casa luminosa en Asunción",
      descripcion: "Casa familiar con patio y ambientes integrados.",
      tipo_operacion: "venta",
      tipo_propiedad: "casa",
      precio: "250000",
      moneda: "USD",
      localidad: "Asunción",
      zona: "Las Lomas",
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
      await screen.findByRole("heading", { name: "Casa luminosa en Asunción" }),
    ).toBeInTheDocument();
    await user.selectOptions(screen.getByLabelText("Operación"), "venta");
    await user.type(screen.getByLabelText("Localidad"), "Asunción");
    await user.click(screen.getByRole("button", { name: "Aplicar" }));

    expect(fetchMock).toHaveBeenLastCalledWith(
      expect.stringContaining(
        "/api/v1/publico/propiedades?tipo_operacion=venta&localidad=Asunci%C3%B3n",
      ),
      expect.objectContaining({
        headers: { Accept: "application/json" },
      }),
    );
  });
});
