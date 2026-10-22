/** Handmade v1 exports replay reported CF shapes; never a NASCAR network test. */
import { test, expect } from "@playwright/test";
import type { Live } from "../../src/types";

test("all series and session types render reported fields and conservative source states", async ({
  page,
}) => {
  await page.goto("/demo/?section=Live%20Timing");
  await expect(page.locator("nrc-leaderboard")).toBeVisible();
  // The backend export is synthetic. Extend the preview's selected series only.
  await page.evaluate(() => {
    const select = document
      .querySelector("nascar-race-center-card")!
      .shadowRoot!.querySelector<HTMLSelectElement>(
        '[aria-label="Selected series"]',
      )!;
    if (![...select.options].some((o) => o.value === "3"))
      select.add(new Option("Truck Series", "3"));
  });
  for (const series of [1, 2, 3]) {
    if (series !== 1)
      await page.getByLabel("Selected series").selectOption(String(series));
    for (const [index, kind] of ["practice", "qualifying", "race"].entries()) {
      const reported: Live = await page.evaluate(
        async ({ series, kind, index }) => {
          const connection = window.nrcDemo.hass.connection;
          const data = structuredClone(connection.live(1).data);
          delete (data as Live & { revision?: number }).revision;
          data.identity = { ...data.identity, series_id: series };
          data.session!.status = kind;
          data.session!.run_type_code = index + 1;
          data.session!.run_name = `Synthetic ${kind}`;
          data.session!.total_laps = kind === "race" ? 100 : null;
          data.session!.laps_remaining = kind === "race" ? 58 : null;
          data.session!.stage = null;
          data.session_state = "activity_unconfirmed";
          data.observation_advancement = "first_observation";
          connection.push(data);
          await window.nrcDemo.card.updateComplete;
          return data;
        },
        { series, kind, index },
      );
      await expect(
        page.getByRole("heading", { name: `Synthetic ${kind}`, exact: true }),
      ).toBeVisible();
      await expect(
        page
          .getByText("Reported session · activity unconfirmed", { exact: true })
          .first(),
      ).toBeVisible();
      await expect(
        page.locator("nrc-leaderboard").getByRole("row"),
      ).toHaveCount(reported.leaderboard!.length + 1);
      await expect(page.locator(".section-head small")).toHaveText(
        "Race 99001 · timing run 7",
      );
      await page.evaluate(
        (data) =>
          window.nrcDemo.hass.connection.push({
            ...data,
            session_state: "active",
            observation_advancement: "observations_changed",
          }),
        reported,
      );
      await expect(
        page.getByText("Fresh source", { exact: true }).first(),
      ).toBeVisible();
      for (const state of ["latest_recorded", "no_active_session"] as const) {
        await page.evaluate(
          ({ data, session_state }) =>
            window.nrcDemo.hass.connection.push({
              ...data,
              session_state,
              session: null,
              leaderboard: null,
            }),
          { data: reported, session_state: state },
        );
        await expect(
          page.getByRole("heading", { name: "No current timing", exact: true }),
        ).toBeVisible();
        for (const name of ["Pits", "Stages", "Points"])
          await page
            .getByRole("button", { name: new RegExp(`^${name} ·`, "i") })
            .click();
        await expect(page.getByRole("alert")).toHaveCount(0);
        await expect(page.locator("nrc-leaderboard")).toHaveCount(0);
      }
    }
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
