import { defineConfig } from "@playwright/test";
type BrowserName = "chromium" | "firefox" | "webkit";
const engines = (process.env.NRC_BROWSERS ?? "chromium,firefox,webkit").split(
  ",",
) as BrowserName[];
export default defineConfig({
  testDir: "test/browser",
  workers: 1,
  projects: engines.map((browserName) => ({
    name: browserName,
    use: {
      browserName,
      ...(browserName === "chromium"
        ? {
            launchOptions: {
              executablePath:
                process.env.CHROMIUM_PATH === "bundled"
                  ? undefined
                  : process.env.CHROMIUM_PATH || "/usr/bin/chromium",
              args: ["--no-sandbox"],
            },
          }
        : {}),
    },
  })),
  use: { baseURL: "http://127.0.0.1:5173" },
  webServer: {
    command: "npm run dev",
    url: "http://127.0.0.1:5173/demo/",
    reuseExistingServer: !process.env.CI,
  },
  reporter: [["list"]],
  outputDir: "test-results",
});
