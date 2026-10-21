/** Test-only adapter over real v1 serializer exports. Not imported by src/card.ts. */
import contract from "./contract.json";
import type {
  Bootstrap,
  Connection,
  Envelope,
  Hass,
  Live,
  Page,
  Unsubscribe,
} from "../src/types";
import { PREFIX } from "../src/api";
const clone = <T>(value: T): T => structuredClone(value);
export const fixtures = contract as unknown as Record<
  string,
  Envelope<Bootstrap | Live | Page>
>;
export class MockConnection implements Connection {
  listeners = new Map<string, Set<() => void>>();
  callbacks = new Map<
    number,
    { callback: (message: unknown) => void; request: Record<string, unknown> }
  >();
  requests: Record<string, unknown>[] = [];
  unsubscribed = 0;
  next = 0;
  delay = 0;
  availability = "ok";
  revision = 1;
  async subscribeMessage<T>(
    callback: (message: T) => void,
    request: Record<string, unknown>,
  ): Promise<Unsubscribe> {
    this.requests.push(request);
    const id = ++this.next;
    this.callbacks.set(id, {
      callback: callback as (message: unknown) => void,
      request,
    });
    if (this.delay)
      await new Promise((resolve) => setTimeout(resolve, this.delay));
    queueMicrotask(() =>
      this.callbacks.get(id)?.callback(this.live(Number(request.series_id))),
    );
    return () => {
      if (this.callbacks.delete(id)) this.unsubscribed++;
    };
  }
  live(series: number): Envelope<Live> {
    const envelope = clone(fixtures.live) as Envelope<Live>;
    const d = envelope.data;
    d.source_updated_at = new Date().toISOString();
    (d as Live & { revision: number }).revision = this.revision;
    if (series !== 1 || this.availability !== "ok") {
      d.identity = { ...d.identity, series_id: series };
      d.availability = series !== 1 ? "not_reported" : this.availability;
      d.stale = this.availability === "stale" ? true : null;
      d.leaderboard = null;
      d.session = null;
      d.leader_driver_id = null;
    }
    return envelope;
  }
  push(change?: Partial<Live>) {
    this.revision++;
    for (const { callback, request } of this.callbacks.values()) {
      const e = this.live(Number(request.series_id));
      Object.assign(e.data, change);
      callback(e);
    }
  }
  addEventListener(type: string, callback: () => void) {
    const set = this.listeners.get(type) ?? new Set();
    set.add(callback);
    this.listeners.set(type, set);
  }
  removeEventListener(type: string, callback: () => void) {
    this.listeners.get(type)?.delete(callback);
  }
  emit(type: "ready" | "disconnected") {
    for (const callback of this.listeners.get(type) ?? []) callback();
  }
}
export class MockHass implements Hass {
  connection = new MockConnection();
  user = { is_admin: true };
  locale = { language: "en-US", time_format: "24" as const };
  config = { time_zone: "America/New_York" };
  requests: Record<string, unknown>[] = [];
  fail?: string;
  async callWS<T>(request: Record<string, unknown>): Promise<T> {
    this.requests.push(clone(request));
    if (this.fail) throw { code: this.fail };
    if (request.type === "config_entries/get")
      return [
        {
          entry_id: "FICTIONAL_ENTRY",
          domain: "nascar_race_center",
          title: "Fictional offline entry",
          state: "loaded",
        },
      ] as T;
    const command = String(request.type).replace(PREFIX, "");
    if (command === "live")
      return this.connection.live(Number(request.series_id)) as T;
    const envelope = clone(fixtures[command]);
    if (!envelope) throw { code: "unknown_command" };
    if (command === "bootstrap") return envelope as T;
    const page = envelope.data as Page;
    if (command === "history" || command === "analytics") {
      if (request.race_id !== 88001 || request.season !== 2024)
        throw { code: "invalid_selection" };
      if (
        command === "analytics" &&
        (request.first_lap !== 1 ||
          request.last_lap !== 48 ||
          JSON.stringify(request.driver_ids) !== "[99002,99003]" ||
          JSON.stringify(request.windows) !== "[5]" ||
          request.time_basis !== "all_available")
      )
        throw { code: "invalid_selection" };
      // Filter explicitly requested historical datasets. Analytics values retain
      // the exact exported query/evidence; preview requires all seven datasets.
      if (command === "history")
        page.records = page.records.filter((row) =>
          (request.datasets as string[]).includes(row.dataset!),
        );
      if (
        command === "analytics" &&
        (request.datasets as string[]).length !== 7
      )
        throw { code: "invalid_selection" };
      if (command === "history")
        page.datasets = page.datasets?.filter((d) =>
          (request.datasets as string[]).includes(d.provenance.dataset),
        );
    }
    if (command === "live_driver" && request.collection === "laps_led")
      page.records = [
        { kind: "laps_led", value: { start_lap: 5, end_lap: 10 } },
      ];
    const offset = Number(request.offset ?? 0),
      limit = Number(request.limit ?? 200);
    const total = page.records.length;
    if (request.snapshot && request.snapshot !== "a".repeat(64))
      throw { code: "snapshot_invalid" };
    page.records = page.records.slice(offset, offset + limit);
    const end = offset + page.records.length;
    page.pagination = {
      offset,
      limit,
      total,
      returned: page.records.length,
      next_offset: end < total ? end : null,
      complete: end >= total,
      snapshot: "a".repeat(64),
    };
    return envelope as T;
  }
}
