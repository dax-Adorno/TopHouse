import { expect, test } from "@playwright/test";

const propertyPage = {
  items: [],
  total: 0,
  offset: 0,
  limit: 9,
};

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/publico/propiedades**", async (route) => {
    await route.fulfill({ json: propertyPage });
  });
  await page.route("**/api/v1/auth/me", async (route) => {
    await route.fulfill({ status: 401, json: { detail: "Unauthorized" } });
  });
});

test("keeps primary pages usable without horizontal overflow", async ({
  page,
}) => {
  for (const path of [
    "/",
    "/propiedades",
    "/admin",
    "/nosotros",
    "/servicios",
    "/proyectos",
    "/obras",
    "/prensa",
    "/blog",
    "/contacto",
  ]) {
    await page.goto(path);
    await expect(page.locator("main")).toBeVisible();
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= window.innerWidth,
      ),
    ).toBe(true);
  }
});

test("exposes primary navigation on compact screens", async ({ page }) => {
  test.skip(
    (page.viewportSize()?.width ?? 0) > 1250,
    "The compact menu is used up to the 1250px breakpoint.",
  );

  await page.goto("/");
  const menuButton = page.getByRole("button", { name: "Menú principal" });
  await expect(menuButton).toBeVisible();
  await expect(menuButton).toHaveAttribute("aria-expanded", "false");

  await menuButton.click();
  await expect(menuButton).toHaveAttribute("aria-expanded", "true");
  await menuButton.press("Escape");
  await expect(menuButton).toHaveAttribute("aria-expanded", "false");
  await expect(menuButton).toBeFocused();
  await menuButton.click();
  await page
    .getByRole("navigation", { name: "Navegación principal" })
    .getByRole("link", { name: "Propiedades", exact: true })
    .click();

  await expect(page).toHaveURL(/\/propiedades$/);
  await expect(menuButton).toHaveAttribute("aria-expanded", "false");
});

test("opens every new screen from navigation", async ({ page }) => {
  await page.goto("/");
  for (const [path, title] of [
    ["nosotros", "Nosotros"],
    ["servicios", "Servicios"],
    ["proyectos", "Proyectos"],
    ["obras", "Obras"],
    ["prensa", "Prensa"],
    ["blog", "Blog"],
    ["contacto", "Contacto"],
  ]) {
    const menu = page.getByRole("button", { name: "Menú principal" });
    if (await menu.isVisible()) await menu.click();
    await page
      .getByRole("navigation", { name: "Navegación principal" })
      .getByRole("link", { name: title, exact: true })
      .click();
    await expect(page).toHaveURL(new RegExp("/" + path + "$"));
    await expect(
      page.getByRole("heading", { level: 1, name: title, exact: true }),
    ).toBeVisible();
    await page.reload();
    await expect(
      page.getByRole("heading", { level: 1, name: title, exact: true }),
    ).toBeVisible();
  }
  await expect(
    page.getByRole("link", { name: "+54 9 2664 32-0295", exact: true }),
  ).toHaveAttribute("href", "tel:+5492664320295");
});
