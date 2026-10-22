import { DashboardClient, DashboardError, errorCode } from "./api";
import type { DataRow, Page, PageCommand, PageSelection } from "./types";
/** At most eight pages (1,600 rows) per open view. Previous pages replay exact offsets. */
export class PageView {
  pages = new Map<number, Page>();
  current?: Page;
  error?: unknown;
  loading = false;
  created = 0;
  private generation = 0;
  private previousOffsets: number[] = [];
  private client?: DashboardClient;
  private drain: Promise<void> = Promise.resolve();
  constructor(
    public command: PageCommand,
    public selection: PageSelection,
    private expectedLive?: { race_id: string | null; run_id: string | null },
  ) {}
  get records(): DataRow[] {
    return [...this.pages.values()]
      .sort((a, b) => a.pagination.offset - b.pagination.offset)
      .flatMap((p) => p.records);
  }
  get expired() {
    return (
      !!this.created &&
      ["history", "analytics"].includes(this.command) &&
      Date.now() - this.created >= 300_000
    );
  }
  get canPrevious() {
    return this.previousOffsets.length > 0;
  }
  invalidate(): Promise<void> {
    const token = this.current?.pagination.snapshot;
    const cleanup =
      token && ["history", "analytics"].includes(this.command)
        ? this.client?.releaseSnapshot(token)
        : undefined;
    const drain = this.drain;
    this.generation++;
    this.loading = false;
    this.pages.clear();
    this.current = undefined;
    this.created = 0;
    this.previousOffsets = [];
    this.error = undefined;
    // Also wait for a late first-page response to release its newly issued token.
    const done = Promise.all([cleanup, drain]).then(() => undefined);
    void done.catch(() => undefined);
    return done;
  }
  async load(
    client: DashboardClient,
    offset = 0,
    restart = false,
  ): Promise<void> {
    if (this.loading) return;
    if (restart) {
      const cleanup = this.invalidate();
      const restarting = this.generation;
      this.loading = true;
      try {
        await cleanup;
      } catch (error) {
        if (restarting === this.generation) {
          this.error = error;
          this.loading = false;
        }
        return;
      }
      if (restarting !== this.generation) return;
      this.loading = false;
    }
    this.client = client;
    const generation = this.generation;
    if (this.expired) {
      this.error = new DashboardError("snapshot_expired");
      return;
    }
    const cached = this.pages.get(offset);
    if (cached) {
      this.current = cached;
      this.error = undefined;
      return;
    }
    this.loading = true;
    this.error = undefined;
    let drained!: () => void;
    this.drain = new Promise<void>((resolve) => {
      drained = resolve;
    });
    try {
      const page = await client.page(
        this.command,
        this.selection,
        offset,
        this.current?.pagination.snapshot,
        () => generation === this.generation,
      );
      if (generation !== this.generation) {
        if (["history", "analytics"].includes(this.command))
          await client.releaseSnapshot(page.pagination.snapshot);
        return;
      }
      if (
        this.expectedLive &&
        ((page.identity?.series_id ??
          (this.expectedLive.race_id === null
            ? this.selection.series_id
            : undefined)) !== this.selection.series_id ||
          (page.identity?.race_id ?? null) !== this.expectedLive.race_id ||
          (page.identity?.run_id ?? null) !== this.expectedLive.run_id)
      )
        throw new DashboardError("snapshot_changed");
      if (!this.created) this.created = Date.now();
      this.pages.set(offset, page);
      this.current = page;
      while (this.pages.size > 8)
        this.pages.delete(this.pages.keys().next().value!);
    } catch (error) {
      if (generation === this.generation) {
        if (errorCode(error) === "snapshot_changed") {
          this.pages.clear();
          this.current = undefined;
          this.previousOffsets = [];
          this.created = 0;
        }
        this.error = error;
      }
    } finally {
      if (generation === this.generation) this.loading = false;
      drained();
    }
  }
  async next(client: DashboardClient) {
    const p = this.current?.pagination;
    if (!p || p.next_offset === null) return;
    const before = p.offset;
    await this.load(client, p.next_offset);
    if (this.current && this.current.pagination.offset !== before)
      this.remember(before);
  }
  async previous(client: DashboardClient) {
    const offset = this.previousOffsets.at(-1);
    if (offset === undefined) return;
    await this.load(client, offset);
    if (this.current?.pagination.offset === offset) this.previousOffsets.pop();
  }
  async jump(client: DashboardClient, offset: number) {
    if (!this.pages.has(offset) || this.loading) return;
    const before = this.current?.pagination.offset;
    await this.load(client, offset);
    if (
      before !== undefined &&
      before !== offset &&
      this.current?.pagination.offset === offset
    )
      this.remember(before);
  }
  private remember(offset: number) {
    this.previousOffsets.push(offset);
    if (this.previousOffsets.length > 64) this.previousOffsets.shift();
  }
}

/** Cards on one socket may offer their own hidden, idle selections for cleanup.
 * Tokens/pages stay with their owning client; active cards and other sockets
 * are never evicted. Registration is removed on card detach or reconnect.
 */
const cleanupOwners = new WeakMap<
  import("./types").Connection,
  Map<string, Set<() => Promise<boolean>>>
>();
export function registerSnapshotCleanup(
  client: DashboardClient,
  cleanup: () => Promise<boolean>,
): () => void {
  let entries = cleanupOwners.get(client.hass.connection);
  if (!entries) {
    entries = new Map();
    cleanupOwners.set(client.hass.connection, entries);
  }
  let owners = entries.get(client.entry);
  if (!owners) {
    owners = new Set();
    entries.set(client.entry, owners);
  }
  owners.add(cleanup);
  return () => {
    owners.delete(cleanup);
    if (!owners.size) entries.delete(client.entry);
  };
}
export async function releaseUnusedSnapshot(
  client: DashboardClient,
): Promise<boolean> {
  const owners = cleanupOwners.get(client.hass.connection)?.get(client.entry);
  for (const cleanup of owners ?? []) if (await cleanup()) return true;
  return false;
}
