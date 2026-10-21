import type {
  Bootstrap,
  Connection,
  Envelope,
  Hass,
  Live,
  Page,
  PageCommand,
  PageSelection,
  Unsubscribe,
} from "./types";
export const PREFIX = "nascar_race_center/dashboard/";
export class DashboardError extends Error {
  constructor(
    public code: string,
    message?: string,
  ) {
    super(message || code);
    this.name = "DashboardError";
  }
}
export function errorCode(error: unknown): string {
  return typeof error === "object" && error !== null && "code" in error
    ? String(error.code)
    : "connection_error";
}
const hints: Record<string, string> = {
  unauthorized:
    "Administrator access is required for dashboard API v1. Sign in with an administrator account.",
  entry_unavailable:
    "This integration entry is missing, unloaded, or restarting. Select a loaded NASCAR Race Center entry, then reconnect.",
  invalid_format:
    "The request or API version is unsupported. Card 0.5 requires dashboard API v1 (Phase 5A).",
  api_version: "Incompatible dashboard API. Card 0.5 requires API v1.",
  unknown_command:
    "Dashboard API is unavailable. Install the Phase 5A integration or newer API v1 implementation.",
  snapshot_expired:
    "This five-minute selection expired. Restart the selection to load a new snapshot.",
  snapshot_invalid:
    "The snapshot is no longer valid on this connection. Restart the selection.",
  snapshot_changed:
    "The source changed while paging. Restart the selection to avoid mixing records.",
  snapshot_limit:
    "Snapshot capacity is in use (two per user, four globally). Reuse an open selection or wait up to five minutes before retrying.",
  request_limit:
    "Too many simultaneous requests. Wait for the current request to finish, then retry.",
  rate_limited: "Request limit reached. Wait at least 10 seconds, then retry.",
  invalid_selection:
    "The selection is invalid or the series is not monitored by this entry.",
  invalid_response: "The API response did not match the documented v1 shape.",
  unsafe_identifier:
    "This identifier cannot be sent losslessly as a JavaScript integer.",
  connection_error:
    "Connection interrupted. Reconnect to Home Assistant or retry.",
  retention_limit:
    "Client retention limit reached. Use the next page to view more records.",
};
export function errorMessage(error: unknown): string {
  const c = errorCode(error);
  return (
    hints[c] ||
    `Data unavailable (${c.replaceAll("_", " ")}). Narrow the selection or retry.`
  );
}
export function requestId(value: string, max = 10_000_000_000): number {
  if (
    !/^\d+$/.test(value) ||
    BigInt(value) < 1n ||
    BigInt(value) > BigInt(max) ||
    BigInt(value) > BigInt(Number.MAX_SAFE_INTEGER)
  )
    throw new DashboardError("unsafe_identifier");
  return Number(value);
}
function object(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
/** HA callWS resolves result and subscribeMessage passes event. Wrappers are accepted for replay tests. */
export function decode<T>(wire: unknown, entry: string): Envelope<T> {
  if (object(wire) && wire.type === "result") {
    if (wire.success === false)
      throw new DashboardError(
        object(wire.error) ? String(wire.error.code) : "invalid_response",
      );
    wire = wire.result;
  } else if (object(wire) && wire.type === "event") wire = wire.event;
  if (!object(wire) || wire.api_version !== 1)
    throw new DashboardError("api_version");
  if (wire.entry_id !== entry || !object(wire.data))
    throw new DashboardError("invalid_response");
  return wire as unknown as Envelope<T>;
}
export function validateLive(data: Live, series: number): Live {
  if (
    data.identity?.series_id !== series ||
    typeof data.availability !== "string" ||
    (data.leaderboard !== null &&
      (!Array.isArray(data.leaderboard) ||
        data.leaderboard.length > 100 ||
        data.leaderboard.some((d) => typeof d.driver_id !== "string")))
  )
    throw new DashboardError("invalid_response");
  // Defensive freshness gate, even if a malformed server supplies stale current rows.
  return data.availability === "ok" && data.stale === false
    ? data
    : { ...data, session: null, leaderboard: null, leader_driver_id: null };
}
/** Queue is shared only for pacing requests on one HA connection. No view state is shared. */
const lanes = new WeakMap<
  Connection,
  Map<string, { tail: Promise<void>; last: number }>
>();
function laneFor(connection: Connection, entry: string) {
  let entries = lanes.get(connection);
  if (!entries) {
    entries = new Map();
    lanes.set(connection, entries);
  }
  let lane = entries.get(entry);
  if (!lane) {
    lane = { tail: Promise.resolve(), last: 0 };
    entries.set(entry, lane);
  }
  return lane;
}
export class DashboardClient {
  private readonly controller = new AbortController();
  dispose() {
    this.controller.abort();
  }
  constructor(
    public hass: Hass,
    public entry: string,
    private active: () => boolean = () => true,
  ) {}
  private async paced<T>(work: () => Promise<T>): Promise<T> {
    const lane = laneFor(this.hass.connection, this.entry);
    const run = lane.tail.then(async () => {
      const delay = Math.max(0, 370 - (Date.now() - lane.last));
      if (this.controller.signal.aborted)
        throw new DashboardError("connection_error");
      if (delay)
        await new Promise<void>((resolve, reject) => {
          const stop = () => {
            clearTimeout(timer);
            reject(new DashboardError("connection_error"));
          };
          const timer = setTimeout(() => {
            this.controller.signal.removeEventListener("abort", stop);
            resolve();
          }, delay);
          this.controller.signal.addEventListener("abort", stop, {
            once: true,
          });
        });
      if (this.controller.signal.aborted || !this.active())
        throw new DashboardError("connection_error");
      lane.last = Date.now();
      return work();
    });
    lane.tail = run.then(
      () => undefined,
      () => undefined,
    );
    return run;
  }
  private message(command: string, params: Record<string, unknown> = {}) {
    return {
      type: PREFIX + command,
      entry_id: this.entry,
      api_version: 1,
      ...params,
    };
  }
  async request<T>(
    command: string,
    params: Record<string, unknown> = {},
  ): Promise<T> {
    const wire = await this.paced(() =>
      this.hass.callWS<unknown>(this.message(command, params)),
    );
    return decode<T>(wire, this.entry).data;
  }
  async bootstrap(): Promise<Bootstrap> {
    const b = await this.request<Bootstrap>("bootstrap");
    if (
      !Array.isArray(b.series_ids) ||
      !b.series_ids.length ||
      b.series_ids.some((s) => ![1, 2, 3].includes(s)) ||
      !Array.isArray(b.favorite_driver_ids) ||
      b.favorite_driver_ids.some((id) => typeof id !== "string") ||
      !b.references ||
      !Array.isArray(b.references.drivers) ||
      !Array.isArray(b.references.tracks) ||
      !Array.isArray(b.navigation) ||
      !Array.isArray(b.upcoming) ||
      !Array.isArray(b.source_state)
    )
      throw new DashboardError("invalid_response");
    return b;
  }
  async live(series_id: number) {
    return validateLive(
      await this.request<Live>("live", { series_id }),
      series_id,
    );
  }
  async subscribe(
    series_id: number,
    callback: (value: Live) => void,
    onError: (error: unknown) => void,
  ): Promise<Unsubscribe> {
    let revision = 0;
    return this.paced(() =>
      this.hass.connection.subscribeMessage<unknown>(
        (wire) => {
          try {
            const envelope = decode<Live>(wire, this.entry);
            const next =
              envelope.revision ??
              (envelope.data as Live & { revision?: number }).revision;
            if (next !== undefined && next <= revision) return;
            if (envelope.data.availability === "entry_unavailable")
              throw new DashboardError("entry_unavailable");
            const value = validateLive(envelope.data, series_id);
            revision = next ?? revision + 1;
            callback(value);
          } catch (error) {
            onError(error);
          }
        },
        this.message("subscribe_live", { series_id }),
      ),
    );
  }
  async page(
    command: PageCommand,
    selection: PageSelection,
    offset = 0,
    snapshot?: string,
  ): Promise<Page> {
    const p = await this.request<Page>(command, {
      ...selection,
      offset,
      limit: 200,
      ...(snapshot ? { snapshot } : {}),
    });
    if (command === "analytics" && p.contract_version !== 1)
      throw new DashboardError("api_version");
    const page = p.pagination;
    if (
      !page ||
      page.offset !== offset ||
      !Array.isArray(p.records) ||
      p.records.length > 200 ||
      page.returned !== p.records.length ||
      !/^([a-f0-9]{64})$/.test(page.snapshot) ||
      !Number.isInteger(page.total) ||
      page.total < offset + p.records.length ||
      (snapshot && page.snapshot !== snapshot) ||
      (page.next_offset !== null &&
        (page.next_offset !== offset + p.records.length ||
          page.next_offset <= offset)) ||
      page.complete !== (page.next_offset === null)
    )
      throw new DashboardError("invalid_response");
    if (command === "live_driver" || command === "live_scoring")
      p.records = p.records.map((row) => ({ ...row, kind: "detail" }));
    return p;
  }
  schedule(selection: PageSelection, offset = 0, snapshot?: string) {
    return this.page("schedule", selection, offset, snapshot);
  }
  history(selection: PageSelection, offset = 0, snapshot?: string) {
    return this.page("history", selection, offset, snapshot);
  }
  analytics(selection: PageSelection, offset = 0, snapshot?: string) {
    return this.page("analytics", selection, offset, snapshot);
  }
  liveDriver(selection: PageSelection, offset = 0, snapshot?: string) {
    return this.page("live_driver", selection, offset, snapshot);
  }
  liveScoring(selection: PageSelection, offset = 0, snapshot?: string) {
    return this.page("live_scoring", selection, offset, snapshot);
  }
}
export async function discoverEntries(hass: Hass) {
  const entries = await hass.callWS<import("./types").Entry[]>({
    type: "config_entries/get",
    domain: "nascar_race_center",
  });
  if (!Array.isArray(entries)) throw new DashboardError("invalid_response");
  return entries.filter((e) => e.domain === "nascar_race_center");
}
