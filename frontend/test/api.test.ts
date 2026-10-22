import { describe, expect, it, test, vi } from "vitest";
import {
  DashboardClient,
  DashboardError,
  decode,
  errorMessage,
  requestId,
  validateLive,
} from "../src/api";
import type { Envelope, Live, Page } from "../src/types";
import { MockHass, fixtures } from "../demo/mock";
import { PageView } from "../src/state";
describe("real v1 fixture envelopes and request contract", () => {
  it("decodes HA unwrapped results and native result/event wrappers", () => {
    const wire = fixtures.live;
    expect(decode(wire, "FICTIONAL_ENTRY")).toEqual(wire);
    expect(
      decode(
        { type: "result", success: true, result: wire },
        "FICTIONAL_ENTRY",
      ),
    ).toEqual(wire);
    expect(decode({ type: "event", event: wire }, "FICTIONAL_ENTRY")).toEqual(
      wire,
    );
    expect(() =>
      decode(
        { type: "result", success: false, error: { code: "unauthorized" } },
        "FICTIONAL_ENTRY",
      ),
    ).toThrow("unauthorized");
  });
  it.each([
    ["version", { ...fixtures.live, api_version: 2 }],
    ["entry", { ...fixtures.live, entry_id: "OTHER" }],
    ["null", null],
    ["data", { ...fixtures.live, data: null }],
  ])("rejects incompatible %s", (_, value) =>
    expect(() => decode(value, "FICTIONAL_ENTRY")).toThrow(DashboardError),
  );
  it.each(["0", "-1", "NaN", "99002.2", "10000000001", "9007199254740993"])(
    "refuses unsafe/bounded integer ID %s",
    (id) => expect(() => requestId(id)).toThrow(DashboardError),
  );
  it("preserves leading-zero car strings and lossless response IDs", () => {
    const d = (fixtures.live.data as Live).leaderboard![1];
    expect(d.car_number).toBe("02");
    expect(typeof d.driver_id).toBe("string");
    expect(requestId("99002")).toBe(99002);
  });
  it("uses authenticated hass.callWS with required entry and version", async () => {
    const hass = new MockHass();
    const c = new DashboardClient(hass, "FICTIONAL_ENTRY");
    await c.bootstrap();
    expect(hass.requests[0]).toEqual({
      type: "nascar_race_center/dashboard/bootstrap",
      entry_id: "FICTIONAL_ENTRY",
      api_version: 1,
    });
  });
  it("rejects series contamination and withholds stale scoring defensively", () => {
    const live = structuredClone(fixtures.live.data) as Live;
    expect(() => validateLive(live, 2)).toThrow();
    live.availability = "stale";
    live.stale = true;
    expect(validateLive(live, 1).leaderboard).toBeNull();
  });
  it("uses one subscription, accepts revisions and unsubscribes", async () => {
    const hass = new MockHass(),
      c = new DashboardClient(hass, "FICTIONAL_ENTRY"),
      callback = vi.fn();
    const unsub = await c.subscribe(1, callback, vi.fn());
    await Promise.resolve();
    expect(callback).toHaveBeenCalledTimes(1);
    hass.connection.push();
    expect(callback).toHaveBeenCalledTimes(2);
    await unsub();
    expect(hass.connection.callbacks.size).toBe(0);
  });
  it.each([
    "unauthorized",
    "entry_unavailable",
    "snapshot_expired",
    "snapshot_limit",
    "rate_limited",
    "invalid_format",
  ])("provides actionable error %s", (code) => {
    expect(errorMessage({ code }).length).toBeGreaterThan(30);
  });
  it("does not send queued work for disposed selections", async () => {
    const hass = new MockHass();
    const c = new DashboardClient(hass, "FICTIONAL_ENTRY", () => false);
    await expect(c.bootstrap()).rejects.toThrow("connection_error");
    expect(hass.requests).toHaveLength(0);
  });
});
describe("immutable paged views", () => {
  const selection = {
    series_id: 1,
    season: 2024,
    race_id: 88001,
    datasets: [
      "weekend",
      "laps",
      "notes",
      "pits",
      "stages",
      "loop",
      "averages",
    ] as const,
  };
  function setup() {
    const hass = new MockHass(),
      client = new DashboardClient(hass, "FICTIONAL_ENTRY");
    const view = new PageView("history", {
      ...selection,
      datasets: [...selection.datasets],
    });
    return { hass, client, view };
  }
  it("pages at 200, uses explicit offsets/token and replays cache without requests", async () => {
    const { hass, client, view } = setup();
    const template = structuredClone(fixtures.history) as Envelope<Page>;
    const all = Array.from({ length: 430 }, (_, i) => ({
      kind: "lap" as const,
      source_index: i,
      driver_id: "99002",
      value: { lap: i, lap_time: 31, lap_speed: null, running_position: 1 },
    }));
    hass.callWS = vi.fn(async <T>(r: Record<string, unknown>) => {
      const wire = structuredClone(template);
      const offset = Number(r.offset ?? 0),
        rows = all.slice(offset, offset + 200),
        end = offset + rows.length;
      wire.data.records = rows;
      wire.data.pagination = {
        offset,
        limit: 200,
        returned: rows.length,
        total: 430,
        next_offset: end < 430 ? end : null,
        complete: end === 430,
        snapshot: "a".repeat(64),
      };
      return wire as T;
    }) as typeof hass.callWS;
    await view.load(client);
    await view.next(client);
    await view.next(client);
    expect(view.records.map((r) => r.source_index)).toEqual(
      Array.from({ length: 430 }, (_, i) => i),
    );
    expect(hass.callWS).toHaveBeenLastCalledWith(
      expect.objectContaining({
        offset: 400,
        limit: 200,
        snapshot: "a".repeat(64),
      }),
    );
    await view.previous(client);
    expect(hass.callWS).toHaveBeenCalledTimes(3);
  });
  it("invalidates responses from old view state", async () => {
    const { hass, client, view } = setup();
    let resolve!: (value: unknown) => void;
    hass.callWS = vi.fn((request: Record<string, unknown>) =>
      String(request.type).endsWith("/release_snapshot")
        ? Promise.resolve({})
        : new Promise((r) => {
            resolve = r;
          }),
    ) as typeof hass.callWS;
    const pending = view.load(client);
    await vi.waitFor(() => expect(resolve).toBeDefined());
    view.invalidate();
    resolve(fixtures.history);
    await pending;
    expect(view.current).toBeUndefined();
    expect(view.pages.size).toBe(0);
  });
  it("keeps expired/limited snapshots explicit, with no automatic retry loop", async () => {
    const { hass, client, view } = setup();
    hass.fail = "snapshot_expired";
    await view.load(client);
    expect((view.error as { code: string }).code).toBe("snapshot_expired");
    expect(hass.requests).toHaveLength(1);
  });
  it("locally prevents expired continuation", async () => {
    const { hass, client, view } = setup();
    await view.load(client);
    view.created = Date.now() - 301000;
    await view.load(client, 200);
    expect((view.error as { code: string }).code).toBe("snapshot_expired");
    expect(hass.requests).toHaveLength(1);
  });
  it("rejects malformed pagination and changed tokens", async () => {
    const { hass, client, view } = setup();
    const wire = structuredClone(fixtures.history) as Envelope<Page>;
    wire.data.pagination.returned = 999;
    hass.callWS = vi.fn(async <T>() => wire as T) as typeof hass.callWS;
    await view.load(client);
    expect((view.error as { code: string }).code).toBe("invalid_response");
  });
  it("limits retention and replays evicted pages from the same snapshot", async () => {
    const { view } = setup();
    const client = {
      page: vi.fn(
        async (
          _command: string,
          _selection: unknown,
          offset: number,
          snapshot?: string,
        ) => {
          expect(snapshot === undefined || snapshot === "a".repeat(64)).toBe(
            true,
          );
          return {
            records: Array.from({ length: 200 }, (_, i) => ({
              kind: "lap" as const,
              source_index: offset + i,
              value: {
                lap: offset + i,
                lap_time: 31,
                lap_speed: null,
                running_position: 1,
              },
            })),
            pagination: {
              offset,
              limit: 200,
              returned: 200,
              total: 2000,
              next_offset: offset + 200 < 2000 ? offset + 200 : null,
              complete: offset === 1800,
              snapshot: "a".repeat(64),
            },
          };
        },
      ),
    } as unknown as DashboardClient;
    await view.load(client);
    for (let i = 0; i < 9; i++) await view.next(client);
    expect(view.pages.size).toBe(8);
    expect(view.records).toHaveLength(1600);
    expect(view.records[0].source_index).toBe(400);
    await view.load(client, 0);
    expect(view.current?.records[0].source_index).toBe(0);
    expect(view.pages.size).toBe(8);
  });
});

describe("connection request budgets", () => {
  it("paces commands across card clients sharing the same connection", async () => {
    vi.useFakeTimers();
    try {
      const hass = new MockHass(),
        timestamps: number[] = [];
      const original = hass.callWS.bind(hass);
      hass.callWS = vi.fn(async <T>(request: Record<string, unknown>) => {
        timestamps.push(Date.now());
        return original<T>(request);
      }) as typeof hass.callWS;
      const a = new DashboardClient(hass, "FICTIONAL_ENTRY"),
        b = new DashboardClient(hass, "FICTIONAL_ENTRY");
      const pending = Promise.all([a.bootstrap(), b.bootstrap(), a.live(1)]);
      await vi.advanceTimersByTimeAsync(1200);
      await pending;
      expect(timestamps).toHaveLength(3);
      expect(timestamps[1] - timestamps[0]).toBeGreaterThanOrEqual(370);
      expect(timestamps[2] - timestamps[1]).toBeGreaterThanOrEqual(370);
    } finally {
      vi.useRealTimers();
    }
  });
  it("cancels pacing timers on disposal", async () => {
    vi.useFakeTimers();
    try {
      const hass = new MockHass(),
        client = new DashboardClient(hass, "FICTIONAL_ENTRY");
      await client.bootstrap();
      const pending = client.live(1).catch((error) => error);
      await vi.advanceTimersByTimeAsync(1);
      client.dispose();
      expect((await pending).code).toBe("connection_error");
      expect(hass.requests).toHaveLength(1);
      expect(vi.getTimerCount()).toBe(0);
    } finally {
      vi.useRealTimers();
    }
  });
});

test("changed stateless schedule snapshots discard assembled pages", async () => {
  const hass = new MockHass(),
    client = new DashboardClient(hass, "FICTIONAL_ENTRY"),
    view = new PageView("schedule", { series_id: 1 });
  await view.load(client);
  expect(view.current).toBeDefined();
  hass.fail = "snapshot_changed";
  await view.load(client, 200);
  expect(view.current).toBeUndefined();
  expect(view.records).toHaveLength(0);
  expect((view.error as { code: string }).code).toBe("snapshot_changed");
});

test("driver detail racing context cannot change behind an open selection", async () => {
  const hass = new MockHass(),
    client = new DashboardClient(hass, "FICTIONAL_ENTRY");
  const view = new PageView(
    "live_driver",
    { series_id: 1, driver_id: 99002, collection: "pit_stops" },
    { race_id: "DIFFERENT_RACE", run_id: "DIFFERENT_RUN" },
  );
  await view.load(client);
  expect(view.current).toBeUndefined();
  expect(view.records).toHaveLength(0);
  expect((view.error as { code: string }).code).toBe("snapshot_changed");
});

test("history pages cannot substitute a different race selection", async () => {
  const hass = new MockHass(),
    client = new DashboardClient(hass, "FICTIONAL_ENTRY");
  const wire = structuredClone(fixtures.history) as Envelope<Page>;
  wire.data.race!.race_id = "OTHER";
  hass.callWS = vi.fn(async <T>() => wire as T) as typeof hass.callWS;
  await expect(
    client.history({
      series_id: 1,
      season: 2024,
      race_id: 88001,
      datasets: ["weekend"],
    }),
  ).rejects.toThrow("invalid_response");
});

describe("snapshot cleanup", () => {
  it("releases a late snapshot after disposal and deduplicates cleanup", async () => {
    const hass = new MockHass();
    const original = hass.callWS.bind(hass);
    let complete!: () => void;
    const gate = new Promise<void>((resolve) => {
      complete = resolve;
    });
    hass.callWS = vi.fn(async <T>(request: Record<string, unknown>) => {
      if (String(request.type).endsWith("/history")) await gate;
      return original<T>(request);
    }) as typeof hass.callWS;
    const client = new DashboardClient(hass, "FICTIONAL_ENTRY");
    const pending = client.history({
      series_id: 1,
      season: 2024,
      race_id: 88001,
      datasets: ["laps"],
    });
    await vi.waitFor(() => expect(hass.callWS).toHaveBeenCalledTimes(1));
    client.dispose();
    complete();
    await expect(pending).rejects.toThrow("connection_error");
    expect(
      hass.requests.filter((r) => String(r.type).endsWith("/release_snapshot")),
    ).toHaveLength(1);
  });
  it("restarts only after releasing the old snapshot and preserves cached reuse", async () => {
    const hass = new MockHass();
    hass.snapshotBudget = true;
    const client = new DashboardClient(hass, "FICTIONAL_ENTRY");
    const view = new PageView("history", {
      series_id: 1,
      season: 2024,
      race_id: 88001,
      datasets: ["laps"],
    });
    await view.load(client);
    const old = view.current!.pagination.snapshot;
    const before = hass.requests.length;
    await view.load(client);
    expect(hass.requests.length).toBe(before);
    await view.load(client, 0, true);
    expect(view.error).toBeUndefined();
    expect(view.current!.pagination.snapshot).not.toBe(old);
    expect(hass.snapshots.size).toBe(1);
    expect(String(hass.requests.at(-2)!.type)).toContain("/release_snapshot");
    await view.invalidate();
    expect(hass.snapshots.size).toBe(0);
  });
});

it.each([null, { series_id: 1, race_id: null, run_id: null }])(
  "accepts an empty no-session detail identity %s",
  async (identity) => {
    const hass = new MockHass();
    const original = hass.callWS.bind(hass);
    hass.callWS = vi.fn(async <T>(request: Record<string, unknown>) => {
      const result = await original<Envelope<Page>>(request);
      result.data.identity = identity;
      result.data.records = [];
      result.data.pagination = {
        offset: 0,
        limit: 200,
        returned: 0,
        total: 0,
        complete: true,
        next_offset: null,
        snapshot: "a".repeat(64),
      };
      return result as T;
    }) as typeof hass.callWS;
    const view = new PageView(
      "live_scoring",
      { series_id: 1, collection: "pits" },
      { race_id: null, run_id: null },
    );
    await view.load(new DashboardClient(hass, "FICTIONAL_ENTRY"));
    expect(view.error).toBeUndefined();
    expect(view.current?.records).toEqual([]);
  },
);

it.each(["race_id", "run_id", "series_id", "disappeared"])(
  "preserves live identity protection when %s changes",
  async (change) => {
    const hass = new MockHass();
    const wire = structuredClone(fixtures.live_driver) as Envelope<Page>;
    const expected = {
      race_id: wire.data.identity!.race_id,
      run_id: wire.data.identity!.run_id,
    };
    if (change === "disappeared") wire.data.identity = null;
    else if (change === "series_id") wire.data.identity!.series_id = 2;
    else wire.data.identity![change as "race_id" | "run_id"] = "changed";
    hass.callWS = vi.fn(async <T>() => wire as T) as typeof hass.callWS;
    const view = new PageView(
      "live_driver",
      { series_id: 1, driver_id: 99002, collection: "pit_stops" },
      expected,
    );
    await view.load(new DashboardClient(hass, "FICTIONAL_ENTRY"));
    expect((view.error as { code: string }).code).toBe("snapshot_changed");
    expect(view.current).toBeUndefined();
  },
);

it("cancels an abandoned page while it is still queued without allocating a token", async () => {
  const hass = new MockHass();
  const client = new DashboardClient(hass, "FICTIONAL_ENTRY");
  await client.bootstrap();
  const view = new PageView("history", {
    series_id: 1,
    season: 2024,
    race_id: 88001,
    datasets: ["laps"],
  });
  const pending = view.load(client);
  await view.invalidate();
  await pending;
  expect(hass.requests.map((r) => String(r.type).split("/").at(-1))).toEqual([
    "bootstrap",
  ]);
  expect(view.current).toBeUndefined();
});

it("coalesces repeated restart clicks while cleanup is pending", async () => {
  const hass = new MockHass();
  hass.snapshotBudget = true;
  const client = new DashboardClient(hass, "FICTIONAL_ENTRY");
  const view = new PageView("history", {
    series_id: 1,
    season: 2024,
    race_id: 88001,
    datasets: ["laps"],
  });
  await view.load(client);
  await Promise.all([view.load(client, 0, true), view.load(client, 0, true)]);
  expect(view.error).toBeUndefined();
  expect(hass.snapshots.size).toBe(1);
  expect(
    hass.requests.filter((r) => String(r.type).endsWith("/history")),
  ).toHaveLength(2);
  expect(
    hass.requests.filter((r) => String(r.type).endsWith("/release_snapshot")),
  ).toHaveLength(1);
  await view.invalidate();
});

it("failed cleanup retires local ownership without accumulating disposal retries", async () => {
  vi.useFakeTimers();
  try {
    const hass = new MockHass();
    const original = hass.callWS.bind(hass);
    let issued = 0;
    hass.callWS = vi.fn(async <T>(request: Record<string, unknown>) => {
      if (String(request.type).endsWith("/release_snapshot"))
        throw { code: "rate_limited" };
      const result = await original<Envelope<Page>>(request);
      result.data.pagination.snapshot = (++issued)
        .toString(16)
        .padStart(64, "0");
      return result as T;
    }) as typeof hass.callWS;
    const client = new DashboardClient(hass, "FICTIONAL_ENTRY");
    for (let i = 0; i < 20; i++) {
      const work = client
        .history({
          series_id: 1,
          season: 2024,
          race_id: 88001,
          datasets: ["laps"],
        })
        .then((page) => client.releaseSnapshot(page.pagination.snapshot))
        .catch((error) => error);
      await vi.advanceTimersByTimeAsync(800);
      expect((await work).code).toBe("rate_limited");
    }
    const before = vi.mocked(hass.callWS).mock.calls.length;
    client.dispose();
    await vi.advanceTimersByTimeAsync(10000);
    expect(hass.callWS).toHaveBeenCalledTimes(before);
  } finally {
    vi.useRealTimers();
  }
});
