import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:4173",
    trace: "on-first-retry",
  },
  webServer: {
    command: "pnpm exec vite preview --host 127.0.0.1 --port 4173",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: !process.env.CI,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "mobile-chrome",
      testMatch: /responsive\.spec\.ts/,
      use: { ...devices["Pixel 7"] },
    },
    {
      name: "tablet",
      testMatch: /responsive\.spec\.ts/,
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 810, height: 1080 },
        hasTouch: true,
        isMobile: true,
      },
    },
  ],
});
