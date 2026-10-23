/** Synthetic normalized replay of owner-reported CF defects. No CF networking. */
import { test, expect, type Page } from "@playwright/test";
import type { Bootstrap, Envelope, Page as DataPage } from "../../src/types";

async function futureSchedule(page: Page) {
  await page.clock.install({ time: new Date("2026-10-22T12:00:00Z") });
  await page.goto("/demo/?section=Race%20Weekend");
  await expect(
    page.getByRole("heading", { name: "Race Weekend", exact: true }),
  ).toBeVisible();
  await page.evaluate(() => {
    const { hass, card } = window.nrcDemo;
    const original = hass.callWS.bind(hass);
    hass.connection.availability = "no_active_session";
    hass.callWS = async <T>(request: Record<string, unknown>): Promise<T> => {
      const result = await original<T>(request);
      if (String(request.type).endsWith("/bootstrap")) {
        const data = (result as Envelope<Bootstrap>).data;
        data.series_ids = [1, 2, 3];
        const base = data.upcoming[0];
        data.upcoming = [1, 2, 3].map((series) => ({
          ...structuredClone(base),
          series_id: series,
          race_id: String(990100 + series),
          name: `Next series ${series} weekend`,
          start_time: "2026-10-25T18:00:00+00:00",
          season: 2026,
          sessions: [
            {
              session_id: "race",
              name: "Future race",
              kind: "race",
              run_type_code: 3,
              start_time: "2026-10-25T18:00:00+00:00",
              end_time: null,
              status: null,
              notes: null,
            },
            {
              session_id: "q",
              name: "Future qualifying",
              kind: "qualifying",
              run_type_code: 2,
              start_time: "2026-10-23T16:30:00+00:00",
              end_time: "2026-10-23T18:00:00+00:00",
              status: null,
              notes: null,
            },
            {
              session_id: "p",
              name: "Future practice",
              kind: "practice",
              run_type_code: 1,
              start_time: "2026-10-23T15:00:00+00:00",
              end_time: "2026-10-23T16:00:00+00:00",
              status: null,
              notes: null,
            },
          ],
        }));
      }
      return result;
    };
    card.setConfig({
      type: "custom:nascar-race-center-card",
      entry_id: "FICTIONAL_ENTRY",
      section: "Race Weekend",
    });
  });
}

test("all national series show the next weekend and chronological sessions above retained history", async ({
  page,
}) => {
  await futureSchedule(page);
  for (const series of [1, 2, 3]) {
    await page.getByLabel("Selected series").selectOption(String(series));
    const upcoming = page.getByRole("region", { name: "Next known weekend" });
    await expect(
      upcoming.getByRole("heading", { name: `Next series ${series} weekend` }),
    ).toBeVisible();
    const text = await upcoming.innerText();
    expect(text.indexOf("Future practice")).toBeLessThan(
      text.indexOf("Future qualifying"),
    );
    expect(text.indexOf("Future qualifying")).toBeLessThan(
      text.indexOf("Future race"),
    );
    expect(text).not.toContain("2024");
    await expect(
      page.getByText(/The retained catalog below also includes past races/),
    ).toBeVisible();
    await expect(page.getByRole("alert")).toHaveCount(0);
  }
  expect(
    await page.evaluate(() =>
      window.nrcDemo.hass.requests.every(
        (r) => !String(r.type).includes("/history"),
      ),
    ),
  ).toBe(true);
});

test("UTC schedule instants display correctly in Eastern Central and Pacific HA timezones", async ({
  page,
}) => {
  await futureSchedule(page);
  for (const [zone, clock] of [
    ["America/New_York", "12:30"],
    ["America/Chicago", "11:30"],
    ["America/Los_Angeles", "09:30"],
  ]) {
    await page.evaluate(
      ({ zone }) => {
        const { hass, card } = window.nrcDemo;
        hass.config.time_zone = zone;
        card.hass = hass;
        card.setConfig({
          type: "custom:nascar-race-center-card",
          entry_id: "FICTIONAL_ENTRY",
          series_id: 3,
          section: "Race Weekend",
        });
      },
      { zone },
    );
    const upcoming = page.getByRole("region", { name: "Next known weekend" });
    await expect(upcoming).toContainText(clock);
    await expect(upcoming).not.toContainText("Time unconfirmed");
  }
});

test("one denied lap-average dataset retains results and shows its HTTP status calmly", async ({
  page,
}) => {
  await page.goto("/demo/?section=History");
  await expect(
    page.getByRole("heading", { name: "History", exact: true }),
  ).toBeVisible();
  await page.evaluate(() => {
    const hass = window.nrcDemo.hass;
    const original = hass.callWS.bind(hass);
    hass.callWS = async <T>(request: Record<string, unknown>): Promise<T> => {
      const result = await original<T>(request);
      if (String(request.type).endsWith("/history")) {
        const page = (result as Envelope<DataPage>).data;
        page.status = "partial";
        page.records = page.records.filter((row) => row.dataset !== "averages");
        for (const dataset of page.datasets ?? [])
          if (dataset.provenance.dataset === "averages") {
            dataset.status = "network_access_failure";
            dataset.reason = "access_denied";
            dataset.provenance.http_status = 403;
          }
        page.pagination.returned = page.records.length;
        page.pagination.total = page.records.length;
        page.pagination.next_offset = null;
        page.pagination.complete = true;
      }
      return result;
    };
  });
  await page
    .getByRole("spinbutton", { name: "Season", exact: true })
    .fill("2024");
  await page
    .getByRole("textbox", { name: "Race ID · manual key" })
    .fill("88001");
  for (const name of ["weekend", "averages"])
    await page.getByRole("checkbox", { name, exact: true }).check();
  await page
    .getByRole("button", { name: "Load race records", exact: true })
    .click();
  await expect(page.getByRole("alert")).toHaveCount(0);
  await expect(page.getByText("partial", { exact: true })).toBeVisible();
  await page
    .locator("summary")
    .filter({ hasText: /averages\s*·\s*network access failure/ })
    .click();
  await expect(page.getByText("403", { exact: true })).toBeVisible();
  await expect(page.getByText("access denied", { exact: true })).toBeVisible();
  await expect(page.getByRole("table", { name: /results/i })).toBeVisible();
});
