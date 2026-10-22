import { afterEach, describe, expect, it } from "vitest";
import { Chart } from "../src/components/chart";
import { Leaderboard } from "../src/components/leaderboard";
import { recordTitle, resultTable } from "../src/components/records";
import { render } from "lit";
import { date, number, numberLocale } from "../src/format";
import { PageView } from "../src/state";
import { fixtures, MockHass } from "../demo/mock";
import type { DashboardClient } from "../src/api";
import type { DataRow, Live, Page } from "../src/types";
const elements: HTMLElement[] = [];
function mount<T extends HTMLElement>(el: T): T {
  document.body.append(el);
  elements.push(el);
  return el;
}
afterEach(() => elements.splice(0).forEach((el) => el.remove()));
describe("timing interactions", () => {
  it("sorts without modifying observations and announces the direction", async () => {
    const board = mount(new Leaderboard());
    const rows = structuredClone((fixtures.live.data as Live).leaderboard!);
    board.rows = rows;
    await board.updateComplete;
    const before = rows.map((r) => r.driver_id);
    const sort =
      board.shadowRoot!.querySelectorAll<HTMLButtonElement>("th button")[2];
    sort.click();
    sort.click();
    await board.updateComplete;
    expect(rows.map((r) => r.driver_id)).toEqual(before);
    expect(
      board.shadowRoot!.querySelector('[role="status"]')?.textContent,
    ).toContain("descending");
    expect(
      board.shadowRoot!.querySelector('[aria-sort="descending"]')?.textContent,
    ).toContain("Driver");
  });
  it("supports arrow/home/end navigation and exposes missing car numbers", async () => {
    const board = mount(new Leaderboard());
    board.rows = structuredClone((fixtures.live.data as Live).leaderboard!);
    board.rows[0].car_number = null;
    board.rows[0].name = "Fictional Very Long Driver Name With Multiple Parts";
    await board.updateComplete;
    const buttons = [
      ...board.shadowRoot!.querySelectorAll<HTMLButtonElement>(
        ".driver-button",
      ),
    ];
    buttons[0].focus();
    buttons[0].dispatchEvent(
      new KeyboardEvent("keydown", { key: "ArrowDown", bubbles: true }),
    );
    expect(board.shadowRoot!.activeElement).toBe(buttons[1]);
    buttons[1].dispatchEvent(
      new KeyboardEvent("keydown", { key: "End", bubbles: true }),
    );
    expect(board.shadowRoot!.activeElement).toBe(buttons.at(-1));
    expect(board.shadowRoot!.querySelector(".car")?.textContent).toBe("—");
  });
});
describe("chart inspection and sparse observations", () => {
  it("preserves null observations for inspection and never bridges a gap", async () => {
    const chart = mount(new Chart());
    chart.rows = (fixtures.analytics.data as Page).records;
    await chart.updateComplete;
    expect(
      chart.shadowRoot!.querySelectorAll("path").length,
    ).toBeGreaterThanOrEqual(2);
    const lap =
      chart.shadowRoot!.querySelectorAll<HTMLSelectElement>("select")[1];
    lap.value = "17";
    lap.dispatchEvent(new Event("change"));
    await chart.updateComplete;
    expect(
      chart.shadowRoot!.querySelector('[role="status"]')?.textContent,
    ).toContain("Missing / excluded observation");
    const next = chart.shadowRoot!.querySelector<HTMLButtonElement>(
      '[aria-label="Next observation"]',
    )!;
    next.click();
    await chart.updateComplete;
    expect(
      chart.shadowRoot!.querySelector('[role="status"]')?.textContent,
    ).toContain("lap 18");
  });
  it("keeps all-null pages accessible without inventing a plot", async () => {
    const chart = mount(new Chart());
    chart.rows = [
      {
        kind: "window",
        driver_id: "99002",
        size: 5,
        value: {
          first_lap: 1,
          last_lap: 5,
          mean: null,
          sample_count: 0,
          minimum: null,
          maximum: null,
        },
      },
    ] as unknown as DataRow[];
    chart.mode = "window";
    await chart.updateComplete;
    expect(chart.shadowRoot!.querySelector("svg")).toBeNull();
    expect(chart.shadowRoot!.querySelector("tbody")?.textContent).toContain(
      "Missing / excluded",
    );
    expect(
      chart.shadowRoot!.querySelector('[role="status"]')?.textContent,
    ).toContain("lap 5");
  });
  it("uses a centered point for a single position observation", async () => {
    const chart = mount(new Chart());
    chart.rows = [
      {
        kind: "samples",
        driver_id: "99002",
        value: { lap: 8, usable_position: 3 },
      },
    ] as DataRow[];
    chart.mode = "position";
    await chart.updateComplete;
    const point = chart.shadowRoot!.querySelector("circle")!;
    expect(point.getAttribute("cx")).toBe("380");
    expect(point.getAttribute("cy")).toBe("135");
  });
  it("discards obsolete point selection when changing datasets", async () => {
    const chart = mount(new Chart());
    chart.rows = (fixtures.analytics.data as Page).records;
    chart.inspected = { id: "99003", lap: 48 };
    await chart.updateComplete;
    chart.rows = [
      {
        kind: "samples",
        driver_id: "99999",
        value: {
          lap: 2,
          valid_time: true,
          included_in_time_basis: true,
          reported_time: 12,
        },
      },
    ] as DataRow[];
    await chart.updateComplete;
    expect(
      chart.shadowRoot!.querySelector('[role="status"]')?.textContent,
    ).toContain("Driver 99999");
    expect(
      chart.shadowRoot!.querySelector('[role="status"]')?.textContent,
    ).not.toContain("99003");
  });
});
describe("history and cached navigation", () => {
  it("identifies rare records without joining commentary or pit identities", () => {
    expect(
      recordTitle({
        kind: "notes",
        value: {
          lap: 3,
          text: "Fictional lap note",
          reported_driver_ids: ["7"],
          note_id: "1",
          flag_code: null,
        },
      }),
    ).toBe("Lap 3 · Fictional lap note");
    const pit = (fixtures.history.data as Page).records.find(
      (r) => r.kind === "pits",
    )!;
    expect(recordTitle(pit)).toContain("NASCAR driver identity unreported");
    expect(
      recordTitle({
        kind: "flags",
        value: { laps_completed: 5, flag_code: 91 },
      }),
    ).toContain("reported flag code 91");
  });
  it("displays reported finishing order while preserving source rows", () => {
    const result = (fixtures.history.data as Page).records.find(
      (r) => r.kind === "result",
    )!;
    const rows = [
      { ...result, value: { ...result.value!, finishing_position: 9 } },
      { ...result, value: { ...result.value!, finishing_position: 2 } },
    ] as DataRow[];
    const host = mount(document.createElement("div"));
    render(resultTable(rows), host);
    expect(host.querySelector("tbody td")?.textContent).toBe("2");
    expect(
      (rows[0] as Extract<DataRow, { kind: "result" }>).value
        ?.finishing_position,
    ).toBe(9);
  });
  it("reopens a retained page without a command and supports returning", async () => {
    let calls = 0;
    const view = new PageView("history", { series_id: 1 });
    const client = {
      page: async (_command: string, _selection: unknown, offset: number) => {
        calls++;
        return {
          records: [],
          pagination: {
            offset,
            returned: 1,
            limit: 200,
            total: 401,
            next_offset: offset < 400 ? offset + 200 : null,
            complete: false,
            snapshot: "a".repeat(64),
          },
        };
      },
    } as unknown as DashboardClient;
    await view.load(client);
    await view.next(client);
    await view.next(client);
    await view.jump(client, 0);
    expect(calls).toBe(3);
    expect(view.current?.pagination.offset).toBe(0);
    await view.previous(client);
    expect(view.current?.pagination.offset).toBe(400);
    expect(calls).toBe(3);
  });
});
describe("Home Assistant formatting preferences", () => {
  for (const [preference, expected] of [
    ["decimal_comma", "1.234,5"],
    ["comma_decimal", "1,234.5"],
    ["space_comma", "1\u202f234,5"],
    ["none", "1234.5"],
  ]) {
    it(`respects ${preference}`, () => {
      const hass = {
        ...new MockHass(),
        callWS: new MockHass().callWS.bind(new MockHass()),
        locale: { language: "en-US", number_format: preference },
      };
      expect(number(1234.5, numberLocale(hass), 1)).toBe(expected);
    });
  }
  it("respects 12/24 hour clocks and never localizes an ambiguous label", () => {
    const hass = new MockHass();
    expect(
      date("2026-03-08T07:30:00Z", {
        ...hass,
        callWS: hass.callWS.bind(hass),
        locale: { language: "en-US", time_format: "12" },
      }),
    ).toContain("3:30 AM");
    expect(date("2026-03-08T07:30:00Z", hass)).toContain("03:30");
    expect(date("2024-10-21 12:30", hass)).toBe("Time unconfirmed");
  });
});
