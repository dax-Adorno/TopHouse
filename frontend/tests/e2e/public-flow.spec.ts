import { expect, test } from "@playwright/test";

const property = {
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
      url: "/src/assets/hero.png",
      url_thumbnail: "/src/assets/hero.png",
      ancho: 1200,
      alto: 800,
      orden: 0,
      es_portada: true,
    },
  ],
  creado_en: "2026-08-21T12:00:00Z",
  actualizado_en: "2026-08-21T12:00:00Z",
};

const propertyPage = {
  items: [property],
  total: 1,
  offset: 0,
  limit: 9,
};

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/publico/propiedades**", async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname.endsWith("/casa-luminosa-merlo")) {
      await route.fulfill({ json: property });
      return;
    }
    await route.fulfill({ json: propertyPage });
  });
});

test("navigates public property discovery flow", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: /Tu próximo lugar/i }),
  ).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Casa luminosa en Merlo" }),
  ).toBeVisible();

  await page.getByRole("link", { name: "Explorar propiedades" }).click();
  await expect(page).toHaveURL(/\/propiedades$/);
  await expect(
    page.getByRole("heading", { name: /Propiedades para tu próxima etapa/i }),
  ).toBeVisible();

  await page.getByLabel("Operación").selectOption("venta");
  await page.getByLabel("Localidad").fill("Merlo");
  await page.getByRole("button", { name: "Aplicar" }).click();

  await page.getByRole("link", { name: /Casa luminosa en Merlo/i }).click();
  await expect(page).toHaveURL(/\/propiedades\/casa-luminosa-merlo$/);
  await expect(
    page.getByRole("heading", { name: /Casa luminosa en Merlo/i }),
  ).toBeVisible();
  await expect(page.getByText("Descripción")).toBeVisible();
  await expect(
    page.getByRole("link", {
      name: "Ver Piedra Blanca, Merlo, San Luis en el mapa",
    }),
  ).toBeVisible();
});
