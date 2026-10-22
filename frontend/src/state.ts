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
  invalidate() {
    this.generation++;
    this.loading = false;
    this.pages.clear();
    this.current = undefined;
    this.created = 0;
    this.previousOffsets = [];
    this.error = undefined;
  }
  async load(
    client: DashboardClient,
    offset = 0,
    restart = false,
  ): Promise<void> {
    if (this.loading) return;
    if (restart) this.invalidate();
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
    try {
      const page = await client.page(
        this.command,
        this.selection,
        offset,
        this.current?.pagination.snapshot,
      );
      if (generation !== this.generation) return;
      if (
        this.expectedLive &&
        (page.identity?.series_id !== this.selection.series_id ||
          page.identity?.race_id !== this.expectedLive.race_id ||
          page.identity?.run_id !== this.expectedLive.run_id)
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
    }
  }
  async next(client: DashboardClient) {
    const p = this.current?.pagination;
    if (!p || p.next_offset === null) return;
    const before = p.offset;
    await this.load(client, p.next_offset);
    if (this.current?.pagination.offset !== before)
      this.previousOffsets.push(before);
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
      this.previousOffsets.push(before);
  }
}
