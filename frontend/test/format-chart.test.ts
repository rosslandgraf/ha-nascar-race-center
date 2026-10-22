import { summaryOptions } from "../src/components/metric-chart";
import { describe, expect, it } from "vitest";
import {
  countdown,
  date,
  flag,
  freshness,
  number,
  sortedDrivers,
} from "../src/format";
import { chartSeries, segments } from "../src/components/chart";
import { fixtures, MockHass } from "../demo/mock";
import type { Live, Page } from "../src/types";
describe("time, units and conservative statuses", () => {
  it("never counts down naive timestamps or past instants", () => {
    expect(countdown("2027-03-01T12:00:00")).toBeNull();
    expect(countdown("2020-01-01T12:00:00Z")).toBeNull();
    expect(
      countdown("2027-03-01T12:00:00Z", Date.parse("2027-03-01T10:30:00Z")),
    ).toBe("1h 30m");
    expect(date("2027-03-01T12:00:00")).toBe("Time unconfirmed");
  });
  it("formats in HA locale and timezone across DST", () => {
    const hass = new MockHass();
    expect(date("2026-03-08T07:30:00Z", hass)).toContain("03:30");
    expect(number(null)).toBe("—");
    expect(number(0)).toBe("0");
    expect(number(1234.5, "none", 1)).toBe("1234.5");
    expect(number(1234.5, "de-DE", 1)).toBe("1.234,5");
  });
  it("keeps unknown flag codes unknown", () => {
    const live = structuredClone(fixtures.live.data) as Live;
    live.session!.flag = null;
    live.session!.flag_state_code = 91;
    expect(flag(live)).toEqual({ text: "Unknown flag (91)", tone: "neutral" });
    live.availability = "freshness_unknown";
    live.stale = null;
    expect(freshness(live).text).toBe("Freshness unknown");
  });
  it("sorts stably and keeps nulls last in either direction", () => {
    const rows = structuredClone((fixtures.live.data as Live).leaderboard!);
    rows[0].gap = null;
    rows[1].gap = 1;
    rows[2].gap = 1;
    expect(sortedDrivers(rows, "gap", true).at(-1)?.driver_id).toBe(
      rows[0].driver_id,
    );
    const ties = sortedDrivers(rows.slice(1, 3), "gap");
    expect(ties.map((r) => r.driver_id)).toEqual(
      rows.slice(1, 3).map((r) => r.driver_id),
    );
    expect(rows[0].gap).toBeNull();
  });
});
describe("chart data is the backend observation basis", () => {
  const rows = (fixtures.analytics.data as Page).records;
  it("breaks lines at missing/invalid laps and absent numbered rows", () => {
    expect(
      segments([
        { lap: 1, value: 3 },
        { lap: 2, value: null },
        { lap: 3, value: 2 },
        { lap: 5, value: 1 },
      ]).map((s) => s.map((p) => p.lap)),
    ).toEqual([[1], [3], [5]]);
  });
  it("uses backend valid_time/included flags and preserves nulls", () => {
    const series = chartSeries(rows, "time");
    expect(series).toHaveLength(2);
    expect(series[0].points.find((p) => p.lap === 17)?.value).toBeNull();
    expect(segments(series[0].points)).toHaveLength(2);
  });
  it("supports positions, consecutive deltas and backend rolling means", () => {
    expect(chartSeries(rows, "position")[0].points[0].value).toBeGreaterThan(0);
    expect(chartSeries(rows, "delta")[0].points[0].value).toBeNull();
    expect(chartSeries(rows, "window")[0].points[0].lap).toBe(5);
  });
});

describe("summary metric comparisons", () => {
  it("retains backend units/classification for mean, median and fastest observations", () => {
    const options = summaryOptions((fixtures.analytics.data as Page).records);
    for (const name of ["mean", "median", "fastest reported lap"]) {
      const option = options.find((o) => o.name === "Lap summary · " + name)!;
      expect(option).toBeDefined();
      expect(option.classification).toBe("derived");
      expect(option.unit).toContain("unverified");
      expect(option.observations).toHaveLength(2);
    }
  });
  it("keeps recorded race/stage/loop/average observations in their own measurement bases", () => {
    const options = summaryOptions((fixtures.analytics.data as Page).records);
    expect(options.some((o) => o.name.startsWith("Race result"))).toBe(true);
    expect(options.some((o) => o.name.includes("stage"))).toBe(true);
    expect(options.some((o) => o.name.startsWith("loop"))).toBe(true);
    expect(options.some((o) => o.name.startsWith("averages"))).toBe(true);
  });
  it("withholds sentinel and conflicting values from charts", () => {
    const options = summaryOptions([
      {
        kind: "performance_reported_metrics",
        driver_id: "99002",
        value: {
          dataset: "averages",
          source_index: 0,
          title: "Example",
          classification: "recorded",
          metrics: [
            {
              field: "candidate",
              value: 999,
              interpretation: "candidate_sentinel",
            },
          ],
        },
      },
      {
        kind: "performance_stages",
        driver_id: "99002",
        value: {
          dataset: "stages",
          number: 1,
          run_namespace: "stage_run",
          run_id: "7",
          position: 1,
          points: 10,
          conflict: true,
        },
      },
    ]);
    expect(
      options.flatMap((o) => o.observations).every((o) => o.value === null),
    ).toBe(true);
  });
});

describe("CF session evidence", () => {
  it.each([
    ["latest_recorded", "Latest recorded session · timing withheld"],
    ["no_active_session", "No current session"],
    ["activity_unconfirmed", "Reported session · activity unconfirmed"],
    ["completed", "Completed session · reported observations"],
    ["observations_unavailable", "Session observations unavailable"],
  ])("keeps %s distinct from fresh active timing", (session_state, text) => {
    const live = structuredClone(fixtures.live.data) as Live;
    live.session_state = session_state;
    expect(freshness(live)).toEqual({ text, tone: "neutral" });
    live.availability = "offline";
    expect(freshness(live).text).toBe("offline");
    live.availability = "stale";
    expect(freshness(live).text).toContain("Stale");
  });
});
