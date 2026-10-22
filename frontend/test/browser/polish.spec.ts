import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { mkdir, writeFile } from "node:fs/promises";
import type { MockHass } from "../../demo/mock";
import type { NascarRaceCenterCard } from "../../src/card";
declare global {
  interface Window {
    nrcDemo: { hass: MockHass; card: NascarRaceCenterCard };
  }
}
const root = "../docs/screenshots/phase5c";
async function open(page: Page, section = "Race Center", extra = "") {
  await page.goto(`/demo/?section=${encodeURIComponent(section)}${extra}`);
  await expect(
    page.getByRole("button", { name: "Live Timing", exact: true }),
  ).toBeVisible();
  if (
    ["Race Center", "Live Timing"].includes(section) &&
    !extra.includes("state=")
  )
    await expect(
      page.getByText("Fictional 300", { exact: true }),
    ).toBeVisible();
}
async function analyze(page: Page) {
  await open(page, "Analytics");
  await page
    .getByRole("spinbutton", { name: "Season", exact: true })
    .fill("2024");
  await page
    .getByRole("textbox", { name: "Race ID · manual key" })
    .fill("88001");
  await page
    .getByRole("textbox", { name: /NASCAR driver IDs/ })
    .fill("99002, 99003");
  await page
    .getByRole("spinbutton", { name: "Last lap", exact: true })
    .fill("48");
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
  await page.getByRole("button", { name: "Analyze selection" }).click();
  await expect(page.locator("nrc-chart").getByRole("img")).toBeVisible();
}
async function noOverflow(page: Page) {
  // A viewport change and native disclosure layout may settle on separate frames.
  await page.evaluate(
    () =>
      new Promise<void>((resolve) =>
        requestAnimationFrame(() => requestAnimationFrame(() => resolve())),
      ),
  );
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(page.viewportSize()!.width);
  const card = page.locator("nascar-race-center-card");
  if (
    (await card.evaluate(
      (el) => el.shadowRoot!.querySelector("ha-card")!.scrollWidth,
    )) > Math.ceil((await card.boundingBox())!.width)
  ) {
    console.log(
      "Card overflow diagnostics",
      await card.evaluate((el) => {
        const edge = el.getBoundingClientRect().right;
        const nodes = [...el.shadowRoot!.querySelectorAll<HTMLElement>("*")];
        for (const item of [...nodes])
          if (item.shadowRoot)
            nodes.push(...item.shadowRoot.querySelectorAll<HTMLElement>("*"));
        const visible = nodes.filter(
          (item) =>
            !item.closest("svg,.table-scroll,.chart-scroll,.comparison-scroll"),
        );
        return {
          elements: visible
            .filter((item) => item.getBoundingClientRect().right > edge + 1)
            .map((item) => ({
              tag: item.tagName,
              class: String(item.className),
              width: item.getBoundingClientRect().width,
              text: item.textContent?.slice(0, 70),
            })),
          text: visible.flatMap((item) =>
            [...item.childNodes].flatMap((node) => {
              if (node.nodeType !== Node.TEXT_NODE || !node.textContent?.trim())
                return [];
              const range = document.createRange();
              range.selectNode(node);
              return [...range.getClientRects()]
                .filter((rect) => rect.right > edge + 1)
                .map((rect) => ({
                  tag: item.tagName,
                  text: node.textContent?.trim().slice(0, 80),
                  right: rect.right,
                }));
            }),
          ),
          owners: nodes
            .filter(
              (item) =>
                item.scrollWidth > item.clientWidth && item.clientWidth > 0,
            )
            .map((item) => ({
              tag: item.tagName,
              class: String(item.className),
              client: item.clientWidth,
              scroll: item.scrollWidth,
              overflow: getComputedStyle(item).overflowX,
            })),
        };
      }),
    );
  }
  expect(
    await card.evaluate(
      (el) => el.shadowRoot!.querySelector("ha-card")!.scrollWidth,
    ),
  ).toBeLessThanOrEqual(Math.ceil((await card.boundingBox())!.width));
}
for (const width of [
  320, 375, 390, 430, 480, 768, 834, 1024, 1280, 1440, 1920,
]) {
  test(`container and viewport ${width}: timing, weekend and overview`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 1000 });
    await open(page, "Live Timing");
    await noOverflow(page);
    const driver = page.locator("nrc-leaderboard .driver-button").first();
    const box = (await driver.boundingBox())!;
    expect(box.height).toBeGreaterThanOrEqual(44);
    expect(box.x + box.width).toBeLessThanOrEqual(width);
    await page
      .getByRole("button", { name: "Race Weekend", exact: true })
      .click();
    await expect(
      page.getByRole("button", { name: "Select race →" }).first(),
    ).toBeVisible();
    await noOverflow(page);
    await page
      .getByRole("button", { name: "Race Center", exact: true })
      .click();
    await page.locator("nascar-race-center-card").evaluate((el) => {
      (el as HTMLElement).style.width = "min(320px, 100%)";
    });
    await noOverflow(page);
    expect(
      (await page
        .getByRole("combobox", { name: "Selected series" })
        .boundingBox())!.width,
    ).toBeGreaterThan(90);
  });
}
for (const [name, width, height, section, compact] of [
  ["phone-overview", 320, 900, "Race Center", false],
  ["phone-timing", 320, 900, "Live Timing", false],
  ["phone-landscape", 844, 390, "Live Timing", true],
  ["tablet-overview", 768, 1024, "Race Center", false],
  ["tablet-weekend", 834, 1112, "Race Weekend", false],
  ["desktop-timing", 1440, 1100, "Live Timing", true],
  ["wall-overview", 1920, 1200, "Race Center", true],
] as const) {
  test(`actual card screenshot: ${name}`, async ({ page }, info) => {
    await page.setViewportSize({ width, height });
    await open(page, section);
    if (name === "wall-overview")
      await page.locator("nascar-race-center-card").evaluate((el) => {
        (el as HTMLElement).style.maxWidth = "none";
      });
    if (section === "Race Weekend")
      await expect(
        page.getByRole("button", { name: "Select race →" }).first(),
      ).toBeVisible();
    if (compact)
      await page
        .getByRole("combobox", { name: "Display density" })
        .selectOption("compact");
    await mkdir(`${root}/${info.project.name}`, { recursive: true });
    await page.screenshot({
      path: `${root}/${info.project.name}/${name}.png`,
      fullPage: true,
    });
    await noOverflow(page);
    expect(
      (
        await new AxeBuilder({ page })
          .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
          .analyze()
      ).violations,
    ).toEqual([]);
  });
}
test.describe("touch and orientation", () => {
  test.use({ hasTouch: true });
  test("mobile columns, pinned identity, detail focus and rotation", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 375, height: 900 });
    await open(page, "Live Timing");
    await page
      .getByRole("button", { name: "All measurements", exact: true })
      .tap();
    await expect(
      page.getByRole("button", { name: "Essential columns" }),
    ).toHaveAttribute("aria-pressed", "true");
    const driver = page.locator("nrc-leaderboard .driver-button").first();
    const before = (await driver.boundingBox())!.x;
    await page.locator("nrc-leaderboard .table-scroll").evaluate((el) => {
      el.scrollLeft = 400;
    });
    expect((await driver.boundingBox())!.x).toBeCloseTo(before, 0);
    await driver.tap();
    await expect(
      page.getByRole("button", { name: "Close", exact: true }),
    ).toBeFocused();
    await page.getByRole("button", { name: "Close", exact: true }).tap();
    await expect(driver).toBeFocused();
    await page.setViewportSize({ width: 844, height: 390 });
    await noOverflow(page);
    await page.setViewportSize({ width: 375, height: 900 });
    await noOverflow(page);
  });
  test("touch chart controls inspect missing observations", async ({
    page,
  }) => {
    await page.setViewportSize({ width: 390, height: 900 });
    await analyze(page);
    const chart = page.locator("nrc-chart");
    await chart
      .getByRole("combobox", { name: "Lap observation" })
      .selectOption("17");
    await expect(chart.getByRole("status")).toContainText("Missing / excluded");
    await chart.getByRole("button", { name: "Next observation" }).tap();
    await expect(chart.getByRole("status")).toContainText("lap 18");
    await noOverflow(page);
  });
});
test("keyboard chart exploration, hover, coverage and cached pages", async ({
  page,
}, info) => {
  await page.setViewportSize({ width: 1440, height: 1100 });
  await analyze(page);
  const chart = page.locator("nrc-chart");
  await chart
    .getByRole("combobox", { name: "Lap observation" })
    .selectOption("17");
  await expect(chart.getByRole("status")).toContainText("Missing / excluded");
  await chart.getByRole("button", { name: "Next observation" }).focus();
  await page.keyboard.press("Enter");
  await expect(chart.getByRole("status")).toContainText("lap 18");
  await chart.locator("circle").first().hover();
  await expect(chart.getByRole("status")).toContainText("lap 1");
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(page.getByText(/Loaded record ranges:/)).toContainText(
    "1–200, 201–287",
  );
  const calls = await page.evaluate(() => window.nrcDemo.hass.requests.length);
  await page
    .getByRole("combobox", { name: "Return to loaded page" })
    .selectOption("0");
  expect(await page.evaluate(() => window.nrcDemo.hass.requests.length)).toBe(
    calls,
  );
  await page.getByRole("button", { name: "History", exact: true }).click();
  await page
    .getByText("Return to a retained selection", { exact: true })
    .click();
  await page.getByRole("button", { name: /Analytics · Cup Series/ }).click();
  expect(await page.evaluate(() => window.nrcDemo.hass.requests.length)).toBe(
    calls,
  );
  await mkdir(`${root}/${info.project.name}`, { recursive: true });
  await page.screenshot({
    path: `${root}/${info.project.name}/desktop-analytics.png`,
    fullPage: true,
  });
});
test("density is local, large field rows stay keyed, and listeners drain after reconnect", async ({
  page,
}, info) => {
  await open(page, "Live Timing", "&bundle=true");
  await page
    .getByRole("combobox", { name: "Display density" })
    .selectOption("compact");
  const result = await page.evaluate(async () => {
    const { hass, card } = window.nrcDemo;
    const Other = customElements.get("nascar-race-center-card")!;
    const other = new Other() as NascarRaceCenterCard;
    other.setConfig({
      type: "custom:nascar-race-center-card",
      entry_id: "FICTIONAL_ENTRY",
    });
    other.hass = hass;
    document.body.append(other);
    // Wait for both cards' initial subscriptions and matching cached schedule lookups.
    for (
      let i = 0;
      i < 50 &&
      (hass.connection.callbacks.size < 2 ||
        hass.requests.filter((r) => String(r.type).endsWith("/schedule"))
          .length < 2);
      i++
    )
      await new Promise((resolve) => setTimeout(resolve, 100));
    await other.updateComplete;
    const independent =
      other
        .shadowRoot!.querySelector("ha-card")!
        .hasAttribute("data-compact") === false;
    const source = hass.connection.live(1).data.leaderboard!;
    const rows = Array.from({ length: 100 }, (_, i) => ({
      ...source[i % source.length],
      driver_id: String(200000 + i),
      position: i + 1,
      name: `Fictional synthetic driver ${i + 1}`,
    }));
    hass.connection.push({ leaderboard: rows, reported_count: 100 });
    await card.updateComplete;
    const tower = card.shadowRoot!.querySelector(
      "nrc-leaderboard",
    )! as HTMLElement & { updateComplete: Promise<boolean> };
    await tower.updateComplete;
    const first = tower.shadowRoot!.querySelector("tbody tr");
    const timings: number[] = [];
    for (let i = 0; i < 100; i++) {
      const start = performance.now();
      hass.connection.push({
        leaderboard: rows.map((r) => ({ ...r, last_lap_time: i + 0.5 })),
        reported_count: 100,
      });
      await card.updateComplete;
      await tower.updateComplete;
      timings.push(performance.now() - start);
    }
    const stable = first === tower.shadowRoot!.querySelector("tbody tr");
    const rowCount = tower.shadowRoot!.querySelectorAll("tbody tr").length;
    const subscriptions = hass.connection.callbacks.size;
    const beforeIdle = hass.requests.length;
    await new Promise((resolve) => setTimeout(resolve, 1000));
    const idleRequests = hass.requests.length - beforeIdle;
    const memory = (
      performance as Performance & { memory?: { usedJSHeapSize: number } }
    ).memory?.usedJSHeapSize;
    other.remove();
    card.remove();
    await new Promise((resolve) => setTimeout(resolve, 50));
    return {
      independent,
      stable,
      rowCount,
      subscriptions,
      idleRequests,
      memory,
      mean_ms: timings.reduce((a, b) => a + b, 0) / timings.length,
      max_ms: Math.max(...timings),
      remaining_subscriptions: hass.connection.callbacks.size,
      remaining_listeners: [...hass.connection.listeners.values()].reduce(
        (n, s) => n + s.size,
        0,
      ),
    };
  });
  expect(result).toMatchObject({
    independent: true,
    stable: true,
    rowCount: 100,
    subscriptions: 2,
    idleRequests: 0,
    remaining_subscriptions: 0,
    remaining_listeners: 0,
  });
  expect(result.max_ms).toBeLessThan(500);
  await mkdir(`${root}/${info.project.name}`, { recursive: true });
  await writeFile(
    `${root}/${info.project.name}/performance.json`,
    JSON.stringify(result, null, 2) + "\n",
  );
});
test("rapid series/run navigation discards driver details and recovers focus", async ({
  page,
}) => {
  await open(page, "Live Timing");
  await page.locator("nrc-leaderboard .driver-button").first().click();
  await page.evaluate(() => {
    const { hass } = window.nrcDemo;
    const live = hass.connection.live(1).data;
    hass.connection.push({
      identity: { ...live.identity, run_id: "FICTIONAL_NEW_RUN" },
      session: {
        ...live.session!,
        status: "qualifying",
        run_name: "Fictional qualifying",
      },
    });
  });
  await expect(
    page.getByRole("button", { name: "Close", exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Live Timing", exact: true }),
  ).toBeFocused();
  for (const series of ["2", "1", "2", "1"])
    await page
      .getByRole("combobox", { name: "Selected series" })
      .selectOption(series);
  await expect(page.getByText("Fictional 300", { exact: true })).toBeVisible();
  await page.evaluate(() =>
    window.nrcDemo.hass.connection.emit("disconnected"),
  );
  await expect(page.getByRole("alert")).toBeVisible();
  await page.evaluate(() => window.nrcDemo.hass.connection.emit("ready"));
  await expect(page.getByText("Fictional 300", { exact: true })).toBeVisible();
  expect(
    await page.evaluate(() => window.nrcDemo.hass.connection.callbacks.size),
  ).toBe(1);
});
for (const state of ["stale", "no_active_session", "not_reported", "offline"]) {
  test(`state screenshot: ${state}`, async ({ page }, info) => {
    await page.setViewportSize({ width: 390, height: 900 });
    await open(page, "Live Timing", `&state=${state}`);
    await expect(
      page.getByText("No current timing", { exact: true }),
    ).toBeVisible();
    await mkdir(`${root}/${info.project.name}`, { recursive: true });
    await page.screenshot({
      path: `${root}/${info.project.name}/${state}.png`,
      fullPage: true,
    });
    expect(
      (await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa"]).analyze())
        .violations,
    ).toEqual([]);
  });
}
test("loading screenshot and long labels at text enlargement", async ({
  page,
}, info) => {
  await page.goto("/demo/?loading=true");
  await expect(
    page.getByText("Preparing your Race Center", { exact: true }),
  ).toBeVisible();
  await mkdir(`${root}/${info.project.name}`, { recursive: true });
  await page.screenshot({
    path: `${root}/${info.project.name}/loading.png`,
    fullPage: true,
  });
  await page.evaluate(() => {
    window.nrcDemo.hass.delay = 0;
  });
  await page
    .getByRole("button", { name: "Live Timing", exact: true })
    .waitFor();
  await page.getByRole("button", { name: "Live Timing", exact: true }).click();
  await page.setViewportSize({ width: 320, height: 900 });
  await page.evaluate(() => {
    const { hass } = window.nrcDemo;
    const rows = hass.connection.live(1).data.leaderboard!;
    rows[0] = {
      ...rows[0],
      car_number: null,
      name: "Fictional Extremely Long Driver Name With Many Components",
    };
    hass.connection.push({ leaderboard: rows });
    window.nrcDemo.card.style.fontSize = "28px";
  });
  await expect(
    page.getByRole("button", { name: /Fictional Extremely Long Driver/ }),
  ).toBeVisible();
  await noOverflow(page);
});
test("light, forced colors, reduced motion and 200% equivalent reflow", async ({
  page,
}, info) => {
  await page.setViewportSize({ width: 640, height: 900 });
  await page.emulateMedia({ reducedMotion: "reduce", colorScheme: "light" });
  await open(page, "Live Timing");
  await page.evaluate(() => {
    for (const [key, value] of Object.entries({
      "--primary-text-color": "#20252a",
      "--secondary-text-color": "#53606b",
      "--accent-color": "#ff9800",
      "--ha-card-background": "#f3f5f7",
    }))
      document.documentElement.style.setProperty(key, value);
  });
  await noOverflow(page);
  expect(
    (
      await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze()
    ).violations,
  ).toEqual([]);
  await mkdir(`${root}/${info.project.name}`, { recursive: true });
  await page.screenshot({
    path: `${root}/${info.project.name}/light-theme.png`,
    fullPage: true,
  });
  await page.emulateMedia({ forcedColors: "active" });
  await page.getByRole("button", { name: "Live Timing", exact: true }).focus();
  expect(
    await page
      .getByRole("button", { name: "Live Timing", exact: true })
      .evaluate((el) => getComputedStyle(el).outlineStyle),
  ).toBe("solid");
  expect(
    await page
      .getByRole("button", { name: "Live Timing", exact: true })
      .evaluate((el) => getComputedStyle(el).transitionDuration),
  ).toBe("0s");
  await noOverflow(page);
});
test("configuration editor remains functional and emits supported configuration", async ({
  page,
}) => {
  await open(page);
  await page.evaluate(async () => {
    const editor = document.createElement(
      "nascar-race-center-card-editor",
    ) as HTMLElement & { hass: MockHass; setConfig(c: unknown): void };
    editor.setConfig({ type: "custom:nascar-race-center-card" });
    editor.hass = window.nrcDemo.hass;
    document.body.append(editor);
  });
  const editor = page.locator("nascar-race-center-card-editor");
  await expect(
    editor.getByRole("option", { name: /Fictional offline entry/ }),
  ).toHaveCount(1);
  await editor
    .getByRole("combobox", { name: "Initial view", exact: true })
    .selectOption("Analytics");
  await expect(
    editor.getByRole("combobox", { name: "Initial view", exact: true }),
  ).toHaveValue("Analytics");
});

test("200 percent CSS zoom reflows without page scrolling", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await open(page, "Live Timing");
  await page.evaluate(() => {
    document.body.style.zoom = "2";
  });
  await noOverflow(page);
  const target = page.locator("nrc-leaderboard .driver-button").first();
  await target.focus();
  await page.keyboard.press("Enter");
  await expect(
    page.getByRole("button", { name: "Close", exact: true }),
  ).toBeFocused();
  await page.keyboard.press("Escape");
  await expect(target).toBeFocused();
});

test("fifteen minutes of virtual idle does not poll or allocate snapshots", async ({
  page,
}) => {
  await page.clock.install();
  await open(page);
  await page.waitForTimeout(1000);
  const before = await page.evaluate(() => window.nrcDemo.hass.requests.length);
  await page.clock.fastForward(15 * 60 * 1000);
  expect(await page.evaluate(() => window.nrcDemo.hass.requests.length)).toBe(
    before,
  );
  expect(
    await page.evaluate(() => window.nrcDemo.hass.connection.callbacks.size),
  ).toBe(1);
});

for (const font of ["default", "DejaVu Sans"]) {
  test(`analytics and summary labels fit narrow card containers${font === "default" ? "" : ` with ${font}`}`, async ({
    page,
  }) => {
    await analyze(page);
    if (font !== "default")
      await page.locator("nascar-race-center-card").evaluate((el, family) => {
        // Match the wider Linux font that exposed WebKit's native select overflow.
        (el as HTMLElement).style.setProperty(
          "--paper-font-body1_-_font-family",
          `"${family}", sans-serif`,
        );
      }, font);
    await page
      .getByText("Coverage and exclusions", { exact: true })
      .first()
      .click();
    for (const width of [320, 375, 390, 480, 834]) {
      await page.setViewportSize({ width, height: 1000 });
      await noOverflow(page);
      const select = page.getByRole("combobox", {
        name: "Metric and measurement basis",
      });
      expect((await select.boundingBox())!.width).toBeLessThan(width - 32);
      // A select's border box can fit while its internal text overflows the label.
      for (const control of [
        page.getByRole("combobox", { name: "Known retained race" }),
        select,
      ]) {
        const label = control.locator("..");
        expect(
          await label.evaluate((el) => el.scrollWidth),
        ).toBeLessThanOrEqual(await label.evaluate((el) => el.clientWidth));
      }
    }
  });
}

test("snapshot capacity explains reuse without allocating another selection", async ({
  page,
}) => {
  await analyze(page);
  await page.getByRole("button", { name: "History", exact: true }).click();
  await page.getByRole("button", { name: "Load race records" }).click();
  await expect(page.getByText(/Records 1–/)).toBeVisible();
  const calls = await page.evaluate(() => window.nrcDemo.hass.requests.length);
  await page.getByRole("checkbox", { name: "notes", exact: true }).check();
  await page.getByRole("button", { name: "Load race records" }).click();
  await expect(page.getByRole("alert")).toContainText(
    "Snapshot capacity is in use",
  );
  expect(await page.evaluate(() => window.nrcDemo.hass.requests.length)).toBe(
    calls,
  );
  await page
    .getByText("Return to a retained selection", { exact: true })
    .click();
  await page.getByRole("button", { name: /Analytics · Cup Series/ }).click();
  await expect(page.getByRole("alert")).toHaveCount(0);
  expect(await page.evaluate(() => window.nrcDemo.hass.requests.length)).toBe(
    calls,
  );
});
