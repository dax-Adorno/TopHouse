import { expect, test } from "@playwright/test";

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

const adminProperty = {
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
  direccion: "Piedra Blanca",
  latitud: "-32.342900",
  longitud: "-65.013900",
  mostrar_ubicacion_exacta: false,
  dormitorios: 3,
  banios: 2,
  superficie_cubierta: "180",
  superficie_total: "420",
  estado: "publicada",
  destacada: true,
  creado_en: "2026-08-21T12:00:00Z",
  actualizado_en: "2026-08-21T12:00:00Z",
};

const adminPropertyPage = {
  items: [adminProperty],
  total: 1,
  offset: 0,
  limit: 100,
};

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({ status: 401, json: { detail: "Unauthorized" } });
  });
  await page.route("**/api/v1/auth/login", async (route) => {
    await route.fulfill({
      json: adminUser,
      headers: {
        "Set-Cookie": "tophouse_csrf=csrf-e2e; Path=/",
      },
    });
  });
  await page.route("**/api/v1/propiedades?limit=100", async (route) => {
    await route.fulfill({ json: adminPropertyPage });
  });
});

test("logs in and opens admin property editing", async ({ page }) => {
  await page.goto("/admin");

  await expect(
    page.getByRole("heading", { name: "Acceso interno" }),
  ).toBeVisible();
  await page.getByLabel("Email").fill(adminUser.email);
  await page.getByLabel("Contraseña").fill("clave-segura");
  await page.getByRole("button", { name: "Ingresar" }).click();

  await expect(
    page.getByRole("heading", { name: "Panel de TopHouse" }),
  ).toBeVisible();
  await expect(page.getByText("TOP-7")).toBeVisible();
  await expect(page.getByText("Casa luminosa en Merlo")).toBeVisible();

  await page.getByLabel("Buscar en inventario").fill("piedra");
  await expect(page.getByText("TOP-7")).toBeVisible();

  await page.getByRole("button", { name: "Editar datos" }).click();
  await expect(
    page.getByRole("heading", { name: "Editar TOP-7" }),
  ).toBeVisible();
  await expect(page.getByLabel("Localidad")).toHaveValue("Merlo");
  await expect(page.getByLabel("Latitud")).toHaveValue("-32.342900");
});
