import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "test/browser",
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:5173",
    browserName: "chromium",
    launchOptions: {
      executablePath:
        process.env.CHROMIUM_PATH === "bundled"
          ? undefined
          : process.env.CHROMIUM_PATH || "/usr/bin/chromium",
      args: ["--no-sandbox"],
    },
  },
  webServer: {
    command: "npm run dev",
    url: "http://127.0.0.1:5173/demo/",
    reuseExistingServer: !process.env.CI,
  },
  reporter: [["list"]],
  outputDir: "test-results",
});
