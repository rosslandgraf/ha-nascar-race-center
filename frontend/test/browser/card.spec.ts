import { test, expect, type Page } from "@playwright/test";
import type { Live, Envelope } from "../../src/types";
import AxeBuilder from "@axe-core/playwright";
import { mkdir } from "node:fs/promises";
const screenshots = "../work/phase5b-regression";
async function open(page: Page, section = "Race Center") {
  await page.goto("/demo/?section=" + encodeURIComponent(section));
  await expect(
    page.getByRole("button", { name: "Live Timing", exact: true }),
  ).toBeVisible();
  if (section === "Race Center" || section === "Live Timing")
    await expect(
      page.getByText("Fictional 300", { exact: true }),
    ).toBeVisible();
}
async function history(page: Page, analytics = false) {
  await open(page, analytics ? "Analytics" : "History");
  await page
    .getByRole("spinbutton", { name: "Season", exact: true })
    .fill("2024");
  await page
    .getByRole("textbox", { name: "Race ID · manual key" })
    .fill("88001");
  for (const name of [
    "weekend",
    "laps",
    "notes",
    "loop",
    "averages",
    "pits",
    "stages",
  ])
    await page.getByRole("checkbox", { name, exact: true }).check();
  if (analytics) {
    await page
      .getByRole("textbox", { name: /NASCAR driver IDs/ })
      .fill("99002, 99003");
    await page
      .getByRole("spinbutton", { name: "Last lap", exact: true })
      .fill("48");
  }
  await page
    .getByRole("button", {
      name: analytics ? "Analyze selection" : "Load race records",
    })
    .click();
  await expect(page.getByText(/Records 1–/)).toBeVisible();
}
test.beforeAll(async () => {
  await mkdir(screenshots, { recursive: true });
});
for (const [name, width, height, section] of [
  ["desktop-overview", 1440, 1100, "Race Center"],
  ["desktop-timing", 1440, 1100, "Live Timing"],
  ["mobile-overview", 375, 1100, "Race Center"],
  ["mobile-timing", 430, 1000, "Live Timing"],
  ["tablet-weekend", 834, 1100, "Race Weekend"],
  ["wall-overview", 1920, 1200, "Race Center"],
] as const) {
  test(name, async ({ page }) => {
    await page.setViewportSize({ width, height });
    await open(page, section);
    if (section === "Race Weekend")
      await expect(
        page.getByRole("button", { name: "Select race →" }).first(),
      ).toBeVisible();
    expect(
      await page.evaluate(() => document.documentElement.scrollWidth),
    ).toBeLessThanOrEqual(width);
    await page.screenshot({
      path: `${screenshots}/${name}.png`,
      fullPage: true,
    });
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
      .analyze();
    expect(results.violations).toEqual([]);
  });
}
test("historical results and progressive disclosure", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1050 });
  await history(page);
  await expect(
    page.getByRole("cell", { name: "007 Fictional Archive Driver" }),
  ).toBeVisible();
  await page.screenshot({
    path: `${screenshots}/desktop-history.png`,
    fullPage: true,
  });
  await page.getByText(/Explore .* records on this page/).click();
  expect(
    (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
      .violations,
  ).toEqual([]);
});
test("analytics charts, pagination, keyboard and reduced motion", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 1150 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await history(page, true);
  expect(
    await page
      .getByRole("button", { name: "Race Center", exact: true })
      .evaluate((el) => getComputedStyle(el).transitionDuration),
  ).toBe("0s");
  await expect(
    page.getByRole("img", { name: /Lap-time progression/ }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(page.getByText(/Records 201–/)).toBeVisible();
  const metric = page.getByRole("combobox", {
    name: "Metric and measurement basis",
  });
  const median = await metric
    .getByRole("option", {
      name: "Lap summary · median · derived",
      exact: true,
    })
    .getAttribute("value");
  await metric.selectOption(median!);
  await expect(
    page.getByRole("img", { name: /Lap summary · median comparison/ }),
  ).toBeVisible();
  await page.screenshot({
    path: `${screenshots}/desktop-analytics.png`,
    fullPage: true,
  });
  await page.getByText("Exact chart data · accessible table").click();
  await page.getByText("Exact chart data · accessible table").press("Enter");
  await page
    .getByRole("combobox", { name: "Chart", exact: true })
    .selectOption("position");
  await expect(
    page.getByRole("img", { name: /Position progression/ }),
  ).toBeVisible();
  expect(
    (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
      .violations,
  ).toEqual([]);
});
test("keyboard navigation and driver disclosure", async ({ page }) => {
  await open(page, "Live Timing");
  await page
    .getByRole("button", { name: "Fictional Driver B", exact: false })
    .focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("button", { name: "Close", exact: true }),
  ).toBeFocused();
  await page.getByRole("button", { name: "Load pit observations" }).click();
  await expect(page.getByText(/Records 1–2 of 2/)).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(
    page.getByRole("button", { name: "Close", exact: true }),
  ).toHaveCount(0);
});
test("explicit access denial and stale source views", async ({ page }) => {
  await page.goto("/demo/?admin=false");
  await expect(page.getByRole("alert")).toContainText(
    "Administrator access is required",
  );
  await page.goto("/demo/?state=stale");
  await expect(
    page.getByText("Stale · timing withheld", { exact: true }),
  ).toBeVisible();
  await expect(page.locator("nrc-leaderboard")).toHaveCount(0);
});
test("mobile analytics controls remain usable at 375 px", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 1000 });
  await history(page, true);
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(375);
  await page
    .getByRole("combobox", { name: "Chart", exact: true })
    .selectOption("delta");
  await expect(
    page.getByRole("img", { name: /Consecutive-lap change/ }),
  ).toBeVisible();
});

test("versioned production bundle, no external requests, and render measurements", async ({
  page,
}, testInfo) => {
  const requests: string[] = [];
  page.on("request", (request) => requests.push(request.url()));
  await page.goto("/demo/?bundle=true&section=Live%20Timing");
  await expect(
    page.getByRole("button", { name: "Fictional Driver P", exact: false }),
  ).toBeVisible();
  const measurements = await page.evaluate(async () => {
    performance.measure("nrc-data-ready", "nrc-mount");
    const demo = (
      window as unknown as {
        nrcDemo: {
          card: HTMLElement;
          hass: {
            connection: {
              push: (change?: Partial<Live>) => void;
              live: (series: number) => Envelope<Live>;
            };
          };
        };
      }
    ).nrcDemo;
    const original = demo.hass.connection.live(1).data.leaderboard!;
    const board = Array.from({ length: 100 }, (_, i) => ({
      ...original[i % original.length],
      driver_id: String(200000 + i),
      name: `Fictional performance driver ${i + 1}`,
      position: i + 1,
    }));
    const timings: number[] = [];
    for (let i = 0; i < 20; i++) {
      const start = performance.now();
      demo.hass.connection.push({ leaderboard: board, reported_count: 100 });
      await (demo.card as HTMLElement & { updateComplete: Promise<boolean> })
        .updateComplete;
      const tower = demo.card.shadowRoot!.querySelector(
        "nrc-leaderboard",
      ) as HTMLElement & { updateComplete: Promise<boolean> };
      await tower.updateComplete;
      timings.push(performance.now() - start);
    }
    return {
      first_render_ms:
        performance.getEntriesByName("nrc-first-render")[0].duration,
      data_ready_ms: performance.getEntriesByName("nrc-data-ready")[0].duration,
      update_mean_ms: timings.reduce((a, b) => a + b, 0) / timings.length,
      update_max_ms: Math.max(...timings),
      rendered_rows: demo.card.shadowRoot
        ?.querySelector("nrc-leaderboard")
        ?.shadowRoot?.querySelectorAll("tbody tr").length,
    };
  });
  expect(
    requests.some((url) => url.includes("nascar-race-center-card-0.6.0.js")),
  ).toBe(true);
  expect(requests.every((url) => new URL(url).hostname === "127.0.0.1")).toBe(
    true,
  );
  expect(measurements.rendered_rows).toBe(100);
  expect(measurements.update_max_ms).toBeLessThan(500);
  await testInfo.attach("production-render-measurements", {
    body: JSON.stringify(measurements, null, 2),
    contentType: "application/json",
  });
  await import("node:fs/promises").then((fs) =>
    fs.writeFile(
      `${screenshots}/measurements.json`,
      JSON.stringify(measurements, null, 2) + "\n",
    ),
  );
});

for (const state of [
  "offline",
  "freshness_unknown",
  "denied",
  "no_active_session",
  "not_reported",
]) {
  test(`explicit source state: ${state}`, async ({ page }) => {
    await page.goto(`/demo/?section=Live%20Timing&state=${state}`);
    await expect(
      page.getByText("No current timing", { exact: true }),
    ).toBeVisible();
    await expect(page.locator("nrc-leaderboard")).toHaveCount(0);
  });
}

test("light Home Assistant theme preserves readable status and timing colors", async ({
  page,
}) => {
  await open(page, "Live Timing");
  await page.evaluate(() => {
    const root = document.documentElement;
    root.style.colorScheme = "light";
    for (const [key, value] of Object.entries({
      "--primary-text-color": "#20252a",
      "--secondary-text-color": "#53606b",
      "--accent-color": "#ff9800",
      "--ha-card-background": "#f3f5f7",
    }))
      root.style.setProperty(key, value);
  });
  expect(
    (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
      .violations,
  ).toEqual([]);
});

test("tab reuse and snapshot expiry restart from offset zero", async ({
  page,
}) => {
  await history(page, true);
  await page.getByRole("button", { name: "History", exact: true }).click();
  await page.getByRole("button", { name: "Analytics", exact: true }).click();
  const calls = () =>
    page.evaluate(() =>
      (
        window as unknown as {
          nrcDemo: { hass: { requests: Record<string, unknown>[] } };
        }
      ).nrcDemo.hass.requests.filter((r) =>
        String(r.type).endsWith("/analytics"),
      ),
    );
  expect(await calls()).toHaveLength(1);
  await page.evaluate(() => {
    (
      window as unknown as { nrcDemo: { hass: { fail?: string } } }
    ).nrcDemo.hass.fail = "snapshot_expired";
  });
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(
    page.getByText("This five-minute selection expired.", { exact: false }),
  ).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);
  await page.evaluate(() => {
    (
      window as unknown as { nrcDemo: { hass: { fail?: string } } }
    ).nrcDemo.hass.fail = undefined;
  });
  await page.getByRole("button", { name: "Restart selection" }).click();
  await expect(page.getByRole("alert")).toHaveCount(0);
  await expect(page.getByText(/Records 1–200 of/)).toBeVisible();
  expect((await calls()).at(-1)).toMatchObject({ offset: 0 });
  expect((await calls()).at(-1)).not.toHaveProperty("snapshot");
});
