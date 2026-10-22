import { test, expect, type Page, type Locator } from "@playwright/test";
import type { MockHass } from "../../demo/mock";
import type { NascarRaceCenterCard } from "../../src/card";
declare global {
  interface Window {
    nrcDemo: { hass: MockHass; card: NascarRaceCenterCard };
  }
}
async function open(page: Page) {
  await page.goto("/demo/?section=History");
  await expect(
    page.getByRole("button", { name: "Load race records" }),
  ).toBeVisible();
  await page.evaluate(() => {
    window.nrcDemo.hass.snapshotBudget = true;
  });
}
async function choose(card: Locator, index: number) {
  await card.evaluate(async (el) => {
    await (el as NascarRaceCenterCard).updateComplete;
  });
  const before = await card.evaluate(
    () =>
      window.nrcDemo.hass.requests.filter((r) =>
        String(r.type).endsWith("/history"),
      ).length,
  );
  await card
    .getByRole("spinbutton", { name: "Season", exact: true })
    .fill("2024");
  await card
    .getByRole("textbox", { name: "Race ID · manual key" })
    .fill("88001");
  for (const [bit, name] of [
    "weekend",
    "laps",
    "notes",
    "loop",
    "averages",
    "pits",
    "stages",
  ].entries())
    await card
      .getByRole("checkbox", { name, exact: true })
      .setChecked(!!(index & (1 << bit)));
  await card.getByRole("button", { name: "Load race records" }).click();
  await expect
    .poll(() =>
      card.evaluate(
        () =>
          window.nrcDemo.hass.requests.filter((r) =>
            String(r.type).endsWith("/history"),
          ).length,
      ),
    )
    .toBeGreaterThan(before);
  await expect(
    card.getByRole("button", { name: "Load race records" }),
  ).toBeEnabled();
  await expect(card.getByRole("alert")).toHaveCount(0);
  await expect(card.getByText(/Records \d+–\d+ of/)).toBeVisible();
}
test("twenty small selections release older snapshots and unload clears retained tokens", async ({
  page,
}) => {
  test.setTimeout(60000);
  await open(page);
  const card = page.locator("nascar-race-center-card");
  for (let index = 1; index <= 20; index++) {
    await choose(card, index);
    expect(
      await page.evaluate(() => window.nrcDemo.hass.snapshots.size),
    ).toBeLessThanOrEqual(2);
    await card.getByRole("button", { name: "Analytics", exact: true }).click();
    await card.getByRole("button", { name: "History", exact: true }).click();
  }
  const count = await page.evaluate(() => window.nrcDemo.hass.requests.length);
  await card.getByRole("button", { name: "Load race records" }).click();
  await expect(
    card.getByRole("button", { name: "Load race records" }),
  ).toBeEnabled();
  expect(await page.evaluate(() => window.nrcDemo.hass.requests.length)).toBe(
    count,
  );
  expect(
    await page.evaluate(
      () =>
        window.nrcDemo.hass.requests.filter((r) =>
          String(r.type).endsWith("/history"),
        ).length,
    ),
  ).toBe(20);
  await page.evaluate(() => window.nrcDemo.card.remove());
  await expect
    .poll(() => page.evaluate(() => window.nrcDemo.hass.snapshots.size))
    .toBe(0);
});

test("two cards replace only their own abandoned snapshots", async ({
  page,
}) => {
  await open(page);
  await choose(page.locator("nascar-race-center-card"), 1);
  await choose(page.locator("nascar-race-center-card"), 4);
  await page.evaluate(() => {
    const Card = customElements.get("nascar-race-center-card")!;
    const second = new Card() as NascarRaceCenterCard;
    second.setConfig({
      type: "custom:nascar-race-center-card",
      entry_id: "FICTIONAL_ENTRY",
      section: "History",
    });
    second.hass = window.nrcDemo.hass;
    document.body.append(second);
  });
  const second = page.locator("nascar-race-center-card").nth(1);
  await expect(
    second.getByRole("button", { name: "Load race records" }),
  ).toBeVisible();
  await choose(second, 2);
  const firstToken = await page.evaluate(
    () => [...window.nrcDemo.hass.snapshots.keys()][0],
  );
  await choose(second, 3);
  expect(
    await page.evaluate(
      (token) => window.nrcDemo.hass.snapshots.has(token),
      firstToken,
    ),
  ).toBe(true);
  expect(await page.evaluate(() => window.nrcDemo.hass.snapshots.size)).toBe(2);
  await page
    .locator("nascar-race-center-card")
    .nth(0)
    .evaluate((el) => el.remove());
  await expect
    .poll(() => page.evaluate(() => window.nrcDemo.hass.snapshots.size))
    .toBe(1);
  await page.locator("nascar-race-center-card").evaluate((el) => el.remove());
  await expect
    .poll(() => page.evaluate(() => window.nrcDemo.hass.snapshots.size))
    .toBe(0);
});

test("no-session pits stages and points stay calm and issue no detail requests", async ({
  page,
}) => {
  await page.goto("/demo/?section=Live%20Timing&state=no_active_session");
  await expect(
    page.getByText(/no active session. Fresh matching observations/i),
  ).toBeVisible();
  await page.evaluate(() =>
    window.nrcDemo.hass.connection.push({
      identity: {
        series_id: 1,
        race_id: null,
        run_id: null,
        season: null,
        season_basis: "not_reported",
      },
    }),
  );
  for (const name of ["pits", "stages", "points"]) {
    await page
      .getByRole("button", { name: new RegExp("^" + name + " ·", "i") })
      .click();
    await expect(
      page.getByText(/No active session. Live observations/),
    ).toBeVisible();
    await expect(page.getByRole("alert")).toHaveCount(0);
    await page.getByRole("button", { name: "Close", exact: true }).click();
  }
  expect(
    await page.evaluate(
      () =>
        window.nrcDemo.hass.requests.filter((r) =>
          /\/live_(driver|scoring)$/.test(String(r.type)),
        ).length,
    ),
  ).toBe(0);
});
