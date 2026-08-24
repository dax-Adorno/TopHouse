import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it } from "vitest";
import type { PublicProperty } from "../types/property";
import { FeaturedCarousel } from "./FeaturedCarousel";

const baseProperty: PublicProperty = {
  id: 1,
  codigo: "TOP-1",
  slug: "casa-uno",
  titulo: "Casa Uno",
  descripcion: "Casa de prueba",
  tipo_operacion: "venta",
  tipo_propiedad: "casa",
  precio: "100000",
  moneda: "USD",
  localidad: "Merlo",
  zona: "Centro",
  dormitorios: 2,
  banios: 1,
  superficie_cubierta: "90",
  superficie_total: "180",
  estado: "publicada",
  destacada: true,
  imagenes: [],
  creado_en: "2026-08-24T12:00:00Z",
  actualizado_en: "2026-08-24T12:00:00Z",
};

const properties = [
  baseProperty,
  {
    ...baseProperty,
    id: 2,
    codigo: "TOP-2",
    slug: "casa-dos",
    titulo: "Casa Dos",
  },
  {
    ...baseProperty,
    id: 3,
    codigo: "TOP-3",
    slug: "casa-tres",
    titulo: "Casa Tres",
  },
];

describe("FeaturedCarousel", () => {
  afterEach(cleanup);

  it("navega con controles y mantiene una sola tarjeta activa", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <FeaturedCarousel properties={properties} />
      </MemoryRouter>,
    );

    expect(screen.getByRole("heading", { name: "Casa Uno" })).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Propiedad destacada anterior" }),
    ).toBeDisabled();

    await user.click(
      screen.getByRole("button", { name: "Siguiente propiedad destacada" }),
    );

    expect(screen.getByRole("heading", { name: "Casa Dos" })).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Mostrar Casa Dos" }),
    ).toHaveAttribute("aria-current", "true");
  });

  it("permite navegar con las flechas del teclado", async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <FeaturedCarousel properties={properties} />
      </MemoryRouter>,
    );

    const carousel = screen.getByRole("region", {
      name: "Propiedades destacadas",
    });
    carousel.focus();
    await user.keyboard("{ArrowRight}{ArrowRight}");

    expect(screen.getByRole("heading", { name: "Casa Tres" })).toBeVisible();
    expect(
      screen.getByRole("button", { name: "Siguiente propiedad destacada" }),
    ).toBeDisabled();
  });
});
