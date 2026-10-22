/** Actual HA subprocesses install only the component tree. All data is fictional. */
import { test, expect } from "@playwright/test";
import { spawn, type ChildProcess } from "node:child_process";
import { once } from "node:events";
import { resolve } from "node:path";
const base = "http://127.0.0.1:18123";
let process: ChildProcess | undefined;
let output = "";
async function stop() {
  if (!process || process.exitCode !== null) {
    process = undefined;
    return;
  }
  const done = once(process, "exit");
  process.kill("SIGTERM");
  const timer = setTimeout(() => process?.kill("SIGKILL"), 10000);
  await done;
  clearTimeout(timer);
  process = undefined;
}
async function start(version = "0.6.0") {
  await stop();
  output = "";
  process = spawn(
    globalThis.process.env.NRC_PYTHON ?? "python",
    [resolve("test/serve-bundled-ha.py"), "--card-version", version],
    { stdio: ["ignore", "pipe", "pipe"] },
  );
  process.stdout?.on("data", (data) => {
    output += String(data);
  });
  process.stderr?.on("data", (data) => {
    output += String(data);
  });
  await expect
    .poll(
      async () => {
        if (process?.exitCode !== null) throw new Error(output);
        try {
          const loader = await fetch(base + "/nascar_race_center/card.js");
          if (loader.status !== 200) return loader.status;
          return (await fetch(base + "/packaging-test")).status;
        } catch {
          return 0;
        }
      },
      {
        timeout: 20000,
        message: "Actual copied HA component must start and serve its loader",
      },
    )
    .toBe(200);
}
test.afterEach(async () => {
  await stop();
});

test("bundled HA code loads once for aliases and multiple browser clients", async ({
  page,
  browser,
}) => {
  test.setTimeout(60000);
  await start();
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const modules: string[] = [];
  page.on("request", (r) => {
    if (r.url().includes("/nascar_race_center/nascar-race-center-card"))
      modules.push(r.url());
  });
  await page.goto(base + "/packaging-test");
  await expect(page.getByText("Card 0.6.0 · API v1")).toBeVisible();
  await page.evaluate(async () => {
    const alias = "/nascar_race_center/card.js?alias=second";
    await import(alias);
  });
  expect(modules).toHaveLength(1);
  expect(modules[0]).toMatch(/0\.6\.0\.js\?v=[a-f0-9]{64}$/);
  const client = await browser.newContext();
  try {
    const second = await client.newPage();
    await second.goto(base + "/packaging-test");
    await expect(second.getByText("Card 0.6.0 · API v1")).toBeVisible();
    expect(
      await second.evaluate(
        () => customElements.get("nascar-race-center-card") !== undefined,
      ),
    ).toBe(true);
  } finally {
    await client.close();
  }
  expect(errors).toEqual([]);
});

test("real HA restart upgrades and rolls back a warm browser at one resource URL", async ({
  page,
}) => {
  test.setTimeout(90000);
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const loaderPath = base + "/nascar_race_center/card.js";
  for (const [index, version] of ["0.6.0", "0.6.1", "0.6.0"].entries()) {
    await start(version); // 0.6.1 is a labeled synthetic build-identity fixture.
    if (index === 0) await page.goto(base + "/packaging-test");
    else await page.reload();
    await expect(page.getByText(`Card ${version} · API v1`)).toBeVisible();
    const loader = await page.request.get(loaderPath);
    expect(loader.headers()["cache-control"]).toBe("no-store");
    expect(await loader.text()).toContain(`card-${version}.js?v=`);
  }
  expect(errors).toEqual([]);
});

test("one-time resource migration preserves existing card choices and unrelated resources", async ({
  page,
}) => {
  test.setTimeout(60000);
  await start();
  const old = "/local/nascar-race-center/nascar-race-center-card-0.5.3.js";
  await page.goto(base + "/packaging-test");
  await page.evaluate((old) => {
    localStorage.setItem("test-resource", old);
    localStorage.setItem(
      "test-resources",
      JSON.stringify([
        { url: old, type: "module" },
        { url: "/local/household.js", type: "module" },
      ]),
    );
    localStorage.setItem(
      "test-card",
      JSON.stringify({
        type: "custom:nascar-race-center-card",
        entry_id: "FICTIONAL_ENTRY",
        series_id: 2,
        title: "Existing NASCAR dashboard",
        section: "Race Center",
      }),
    );
  }, old);
  await page.reload();
  await expect(page.getByText("Card 0.5.3 · API v1")).toBeVisible();
  // Models the documented owner edit to one resource, never HA private storage.
  await page.evaluate(() => {
    const resources = JSON.parse(localStorage.getItem("test-resources")!);
    resources[0].url = "/nascar_race_center/card.js";
    localStorage.setItem("test-resources", JSON.stringify(resources));
    localStorage.setItem("test-resource", resources[0].url);
  });
  await page.reload();
  await expect(page.getByText("Card 0.6.0 · API v1")).toBeVisible();
  await expect(
    page.getByRole("heading", {
      name: "Existing NASCAR dashboard",
      exact: true,
    }),
  ).toBeVisible();
  await expect(page.getByLabel("Selected series")).toHaveValue("2");
  expect(
    await page.evaluate(
      () => JSON.parse(localStorage.getItem("test-card")!).entry_id,
    ),
  ).toBe("FICTIONAL_ENTRY");
  expect(
    await page.evaluate(
      () => JSON.parse(localStorage.getItem("test-resources")!)[1],
    ),
  ).toEqual({ url: "/local/household.js", type: "module" });
});
