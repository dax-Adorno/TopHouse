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
  for (const path of ["/", "/propiedades", "/admin"]) {
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
    (page.viewportSize()?.width ?? 0) > 800,
    "The compact menu is only used up to the 800px breakpoint.",
  );

  await page.goto("/");
  const menuButton = page.getByRole("button", { name: "Menú principal" });
  await expect(menuButton).toBeVisible();
  await expect(menuButton).toHaveAttribute("aria-expanded", "false");

  await menuButton.click();
  await expect(menuButton).toHaveAttribute("aria-expanded", "true");
  await page.getByRole("link", { name: "Propiedades", exact: true }).click();

  await expect(page).toHaveURL(/\/propiedades$/);
  await expect(menuButton).toHaveAttribute("aria-expanded", "false");
});
