import { LitElement, html, nothing } from "lit";
import type {
  Bootstrap,
  CardConfig,
  Driver,
  Entry,
  Hass,
  Live,
  RaceSummary,
  PageSelection,
  Section,
  Unsubscribe,
} from "./types";
import { DATASETS, SECTIONS, SERIES } from "./types";
import {
  DashboardClient,
  DashboardError,
  discoverEntries,
  errorMessage,
  errorCode,
  requestId,
} from "./api";
import {
  countdown,
  date,
  flag,
  freshness,
  instant,
  label,
  number,
  numberLocale,
} from "./format";
import {
  PageView,
  registerSnapshotCleanup,
  releaseUnusedSnapshot,
} from "./state";
import { messages } from "./messages";
import { styles } from "./styles";
import {
  evidence,
  metricCard,
  records,
  resultTable,
  values,
} from "./components/records";
import "./components/leaderboard";
import "./components/chart";
import "./components/metric-chart";
import type { ChartMode } from "./components/chart";
import "./editor";
export const VERSION = "0.5.2";
export class NascarRaceCenterCard extends LitElement {
  static styles = styles;
  private config: CardConfig = { type: "custom:nascar-race-center-card" };
  private hostHass?: Hass;
  private signature = "";
  private epoch = 0;
  private liveEpoch = 0;
  private bootPending = false;
  private client?: DashboardClient;
  private unsubscribe?: Unsubscribe;
  private liveChain: Promise<void> = Promise.resolve();
  private listening?: Hass["connection"];
  private clock?: ReturnType<typeof setInterval>;
  private bootstrapData?: Bootstrap;
  private liveData?: Live;
  private currentRace?: RaceSummary;
  private entries: Entry[] = [];
  private loading = false;
  private error?: unknown;
  private section: Section = "Race Center";
  private series = 1;
  private schedules = new Map<number, PageView>();
  private snapshots = new Map<string, PageView>();
  private history?: PageView;
  private analytics?: PageView;
  private detail?: PageView;
  private detailDriver?: Driver;
  private detailFocus?: HTMLElement;
  private detailError?: unknown;
  private detailEmpty?: string;
  private submitting = false;
  private unregisterSnapshots?: () => void;
  private formError?: unknown;
  private compact = false;
  private historyKind = "all";
  private chartMode: ChartMode = "time";
  private chartWindow = 5;
  private season = new Date().getFullYear();
  private raceId = "";
  private ready = () => {
    this.scheduleStart();
  };
  private disconnected = () => {
    this.clearRuntime();
    this.error = new DashboardError("connection_error");
    this.requestUpdate();
  };
  static getConfigElement() {
    return document.createElement("nascar-race-center-card-editor");
  }
  static getStubConfig() {
    return { type: "custom:nascar-race-center-card", section: "Race Center" };
  }
  static getDefaultConfig() {
    return this.getStubConfig();
  }
  getCardSize() {
    return 10;
  }
  getGridOptions() {
    return { columns: "full", rows: "auto", min_columns: 6, min_rows: 6 };
  }
  setConfig(config: CardConfig) {
    if (
      !config ||
      (config.entry_id !== undefined &&
        (typeof config.entry_id !== "string" ||
          !config.entry_id.trim() ||
          config.entry_id.length > 128))
    )
      throw new Error("entry_id must be a nonempty integration entry ID.");
    if (config.series_id !== undefined && ![1, 2, 3].includes(config.series_id))
      throw new Error("series_id must be 1, 2, or 3.");
    if (config.section !== undefined && !SECTIONS.includes(config.section))
      throw new Error("Unknown Race Center section.");
    this.config = { ...config };
    this.section = config.section ?? "Race Center";
    this.clearRuntime();
    this.scheduleStart();
    this.requestUpdate();
  }
  set hass(hass: Hass | undefined) {
    if (!hass) return;
    const connectionChanged = this.hostHass?.connection !== hass.connection;
    const signature = JSON.stringify([
      hass.user?.is_admin,
      hass.locale,
      hass.config?.time_zone,
    ]);
    const changed = signature !== this.signature;
    this.signature = signature;
    this.hostHass = hass;
    if (connectionChanged) {
      this.unlisten();
      this.clearRuntime();
      if (this.isConnected) {
        this.listen();
        this.scheduleStart();
      }
    } else if (changed && this.isConnected) this.scheduleStart();
    if (changed) this.requestUpdate();
  }
  get hass() {
    return this.hostHass;
  }
  connectedCallback() {
    super.connectedCallback();
    this.listen();
    this.scheduleStart();
    this.clock = setInterval(() => {
      if (this.section === "Race Center") this.requestUpdate();
    }, 60_000);
  }
  disconnectedCallback() {
    super.disconnectedCallback();
    this.unlisten();
    this.clearRuntime();
    if (this.clock) clearInterval(this.clock);
    this.clock = undefined;
  }
  private listen() {
    if (!this.hostHass || this.listening) return;
    this.listening = this.hostHass.connection;
    this.listening.addEventListener("ready", this.ready);
    this.listening.addEventListener("disconnected", this.disconnected);
  }
  private unlisten() {
    this.listening?.removeEventListener("ready", this.ready);
    this.listening?.removeEventListener("disconnected", this.disconnected);
    this.listening = undefined;
  }
  private clearRuntime() {
    this.epoch++;
    this.stopLive();
    this.unregisterSnapshots?.();
    this.unregisterSnapshots = undefined;
    this.client?.dispose();
    this.client = undefined;
    this.currentRace = undefined;
    this.detail?.invalidate();
    this.bootstrapData = undefined;
    this.liveData = undefined;
    this.loading = false;
    this.error = undefined;
    this.formError = undefined;
    this.detail = undefined;
    this.detailDriver = undefined;
    this.detailError = undefined;
    this.detailEmpty = undefined;
    this.detailFocus = undefined;
    for (const p of [...this.schedules.values(), ...this.snapshots.values()])
      p.invalidate();
    this.schedules.clear();
    this.snapshots.clear();
    this.history = undefined;
    this.analytics = undefined;
  }
  private stopLive() {
    this.liveEpoch++;
    this.liveData = undefined;
    this.currentRace = undefined;
    const unsub = this.unsubscribe;
    this.unsubscribe = undefined;
    if (unsub)
      this.liveChain = this.liveChain.then(async () => {
        try {
          await unsub();
        } catch {
          /* Socket may already be closed. */
        }
      });
  }
  private scheduleStart() {
    if (this.bootPending || !this.isConnected || !this.hostHass) return;
    this.bootPending = true;
    queueMicrotask(() => {
      this.bootPending = false;
      if (this.isConnected) void this.start();
    });
  }
  private async start() {
    this.clearRuntime();
    const epoch = this.epoch;
    const hass = this.hostHass!;
    if (hass.user?.is_admin === false) {
      this.error = new DashboardError("unauthorized");
      this.requestUpdate();
      return;
    }
    this.loading = true;
    this.requestUpdate();
    try {
      if (!this.config.entry_id) {
        const entries = await discoverEntries(hass);
        if (epoch !== this.epoch) return;
        this.entries = entries;
        return;
      }
      const client = new DashboardClient(
        hass,
        this.config.entry_id,
        () => epoch === this.epoch && this.isConnected,
      );
      this.client = client;
      this.unregisterSnapshots = registerSnapshotCleanup(client, async () => {
        if (epoch !== this.epoch) return false;
        const visible =
          this.section === "History"
            ? this.history
            : this.section === "Analytics"
              ? this.analytics
              : undefined;
        const idle = [...this.snapshots].find(
          ([, view]) => view !== visible && !view.loading,
        );
        if (!idle) return false;
        await this.discardSnapshot(...idle);
        this.requestUpdate();
        return true;
      });
      const data = await client.bootstrap();
      if (epoch !== this.epoch) return;
      this.bootstrapData = data;
      this.series =
        this.config.series_id && data.series_ids.includes(this.config.series_id)
          ? this.config.series_id
          : data.series_ids[0];
      this.setDefaultRace();
      this.syncLive();
      if (this.section === "Race Weekend") void this.loadSchedule();
    } catch (error) {
      if (epoch === this.epoch) this.error = error;
    } finally {
      if (epoch === this.epoch) {
        this.loading = false;
        this.requestUpdate();
      }
    }
  }
  private setDefaultRace() {
    const b = this.bootstrapData;
    const nav = b?.navigation.find((n) => n.series_id === this.series);
    const next = b?.upcoming.find((r) => r.series_id === this.series);
    this.season =
      next?.season ?? nav?.seasons.at(-1) ?? new Date().getFullYear();
    this.raceId = next?.race_id ?? "";
  }
  private syncLive() {
    this.stopLive();
    const gen = this.liveEpoch;
    const client = this.client;
    if (!client || !["Race Center", "Live Timing"].includes(this.section))
      return;
    this.liveChain = this.liveChain.then(async () => {
      if (gen !== this.liveEpoch || !this.isConnected) return;
      try {
        const unsub = await client.subscribe(
          this.series,
          (value) => {
            if (gen !== this.liveEpoch) return;
            const old = this.liveData?.identity,
              next = value.identity;
            if (
              (old &&
                (old.race_id !== next.race_id || old.run_id !== next.run_id)) ||
              value.availability !== "ok"
            )
              this.closeDetail(false);
            if (value.session && (!old || old.race_id !== next.race_id))
              void this.resolveCurrentRace(value, gen);
            this.liveData = value;
            this.error = undefined;
            this.requestUpdate();
          },
          (error) => {
            if (gen === this.liveEpoch) {
              this.error = error;
              this.liveData = undefined;
              this.requestUpdate();
            }
          },
        );
        if (gen !== this.liveEpoch || !this.isConnected) await unsub();
        else this.unsubscribe = unsub;
      } catch (error) {
        if (gen === this.liveEpoch) {
          this.error = error;
          this.requestUpdate();
        }
      }
    });
  }
  private async resolveCurrentRace(live: Live, gen: number) {
    this.currentRace = undefined;
    const id = live.identity.race_id;
    if (!id || !this.client) return;
    const known = this.bootstrapData?.upcoming.find(
      (r) => r.series_id === this.series && r.race_id === id,
    );
    if (known) {
      this.currentRace = known;
      return;
    }
    try {
      const page = await this.client.schedule({
        series_id: this.series,
        race_id: requestId(id),
        ...(live.identity.season ? { season: live.identity.season } : {}),
      });
      if (gen !== this.liveEpoch) return;
      const row = page.records.find(
        (r) => r.kind === "race" && r.value?.race_id === id,
      );
      if (row?.kind === "race" && row.value) {
        const sessions = page.records
          .filter((r) => r.kind === "session" && r.race_id === id)
          .flatMap((r) =>
            r.kind === "session" && r.value && "session_id" in r.value
              ? [r.value]
              : [],
          );
        this.currentRace = { ...row.value, sessions };
        this.requestUpdate();
      }
    } catch {
      /* Missing current-event metadata stays unknown; live timing remains independent. */
    }
  }
  private formatNumber(
    value: number | null | undefined,
    _locale?: string,
    digits = 0,
  ) {
    return number(value, numberLocale(this.hass), digits);
  }
  private navigate(section: Section) {
    if (section === this.section) return;
    const wasLive = ["Race Center", "Live Timing"].includes(this.section);
    this.section = section;
    const retained =
      section === "History"
        ? this.history
        : section === "Analytics"
          ? this.analytics
          : undefined;
    if (retained) {
      const key = [...this.snapshots].find(
        ([, view]) => view === retained,
      )?.[0];
      if (key) {
        this.snapshots.delete(key);
        this.snapshots.set(key, retained);
      }
    }
    this.closeDetail(false);
    if (wasLive !== ["Race Center", "Live Timing"].includes(section))
      this.syncLive();
    if (section === "Race Weekend") void this.loadSchedule();
    this.requestUpdate();
  }
  private selectSeries(series: number) {
    if (series === this.series) return;
    this.series = series;
    this.liveData = undefined;
    this.currentRace = undefined;
    this.error = undefined;
    this.closeDetail(false);
    this.setDefaultRace();
    this.history = undefined;
    this.analytics = undefined;
    this.formError = undefined;
    this.syncLive();
    if (this.section === "Race Weekend") void this.loadSchedule();
    this.requestUpdate();
  }
  private chooseEntry(entry_id: string) {
    this.setConfig({ ...this.config, entry_id });
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: this.config },
        bubbles: true,
        composed: true,
      }),
    );
  }
  private async loadSchedule() {
    if (!this.client) return;
    let view = this.schedules.get(this.series);
    if (!view) {
      view = new PageView("schedule", { series_id: this.series });
      this.schedules.set(this.series, view);
    }
    if (!view.current && !view.loading) {
      const task = view.load(this.client);
      this.requestUpdate();
      await task;
      this.requestUpdate();
    }
  }
  private async page(
    view: PageView,
    direction: "next" | "previous" | "retry" | "restart",
  ) {
    if (!this.client) return;
    const promise =
      direction === "next"
        ? view.next(this.client)
        : direction === "previous"
          ? view.previous(this.client)
          : view.load(
              this.client,
              direction === "restart"
                ? 0
                : (view.current?.pagination.offset ?? 0),
              direction === "restart",
            );
    this.requestUpdate();
    await promise;
    this.requestUpdate();
  }
  private async openDriver(driver: Driver, event?: Event) {
    this.closeDetail(false);
    this.detailDriver = driver;
    this.detailFocus = event
      ?.composedPath()
      .find((t) => t instanceof HTMLButtonElement) as HTMLElement | undefined;
    this.requestUpdate();
    await this.updateComplete;
    (this.renderRoot.querySelector(".detail-close") as HTMLElement)?.focus();
  }
  private closeDetail(restore = true) {
    this.detail?.invalidate();
    this.detail = undefined;
    this.detailDriver = undefined;
    this.detailError = undefined;
    this.detailEmpty = undefined;
    if (restore) this.detailFocus?.focus();
    else if (
      this.renderRoot
        .querySelector(".detail-panel")
        ?.contains(this.shadowRoot?.activeElement ?? null)
    )
      (
        this.renderRoot.querySelector(
          '.nav [aria-current="page"]',
        ) as HTMLElement
      )?.focus();
    this.detailFocus = undefined;
    this.requestUpdate();
  }
  private async loadDetail(collection: string, scoring = false) {
    if (!this.client) return;
    if (
      !this.liveData?.identity.race_id ||
      this.liveData.availability !== "ok"
    ) {
      this.closeDetail(false);
      this.detailEmpty =
        this.liveData?.availability === "no_active_session"
          ? "No active session. Live observations will be available when a matching race is reported."
          : "Live observations are unavailable for the current source. Wait for a matching, fresh race observation.";
      this.requestUpdate();
      return;
    }
    const epoch = this.epoch;
    try {
      this.detailError = undefined;
      this.detailEmpty = undefined;
      const selection: PageSelection = { series_id: this.series, collection };
      if (!scoring)
        selection.driver_id = requestId(
          this.detailDriver!.driver_id,
          Number.MAX_SAFE_INTEGER,
        );
      const view = new PageView(
        scoring ? "live_scoring" : "live_driver",
        selection,
        this.liveData?.identity,
      );
      this.detail?.invalidate();
      this.detail = view;
      const task = view.load(this.client);
      this.requestUpdate();
      await task;
      if (epoch === this.epoch) this.requestUpdate();
    } catch (error) {
      if (epoch === this.epoch) {
        this.detailError = error;
        this.requestUpdate();
      }
    }
  }
  private async submit(event: SubmitEvent, analytics = false) {
    event.preventDefault();
    if (!this.client || this.submitting) return;
    this.submitting = true;
    const client = this.client;
    const epoch = this.epoch;
    const form = event.target as HTMLFormElement;
    const data = new FormData(form);
    try {
      this.formError = undefined;
      const season = Number(data.get("season"));
      if (!Number.isInteger(season) || season < 1948 || season > 9999)
        throw new DashboardError("invalid_selection");
      const raceId = String(data.get("race"));
      const race = requestId(raceId);
      const datasets = data
        .getAll("dataset")
        .map(String)
        .filter((v): v is (typeof DATASETS)[number] =>
          DATASETS.includes(v as (typeof DATASETS)[number]),
        );
      if (!datasets.length) throw new DashboardError("invalid_selection");
      const selection: PageSelection = {
        series_id: this.series,
        season,
        race_id: race,
        datasets,
      };
      if (analytics) {
        const ids = String(data.get("drivers"))
          .split(",")
          .map((v) => v.trim())
          .filter(Boolean);
        if (!ids.length || ids.length > 8 || new Set(ids).size !== ids.length)
          throw new DashboardError("invalid_selection");
        const first = Number(data.get("first")),
          last = Number(data.get("last"));
        const windows = data.getAll("window").map(Number);
        if (
          !Number.isInteger(first) ||
          !Number.isInteger(last) ||
          first < 0 ||
          last > 1e10 ||
          last < first ||
          last - first + 1 > 5000 ||
          ids.length * (last - first + 1) * windows.length > 60000
        )
          throw new DashboardError("invalid_selection");
        Object.assign(selection, {
          driver_ids: ids.map((v) => requestId(v)),
          first_lap: first,
          last_lap: last,
          windows,
          time_basis: String(data.get("basis")),
        });
      }
      const command = analytics ? "analytics" : "history";
      const key = command + JSON.stringify(selection);
      let view = this.snapshots.get(key);
      if (!view) {
        for (const [k, v] of this.snapshots)
          if (v.expired || (!v.loading && !v.current))
            await this.discardSnapshot(k, v);
        if (this.snapshots.size >= 2) {
          const [k, v] =
            [...this.snapshots].find(
              ([, candidate]) => candidate.command === command,
            ) ?? this.snapshots.entries().next().value!;
          await this.discardSnapshot(k, v);
        }
        if (epoch !== this.epoch) return;
        view = new PageView(command, selection);
        this.snapshots.set(key, view);
      }
      // Touch the retained selection so eviction keeps the most recently used.
      this.snapshots.delete(key);
      this.snapshots.set(key, view);
      if (analytics) {
        this.analytics = view;
        if (!selection.windows?.includes(this.chartWindow))
          this.chartWindow = selection.windows?.[0] ?? 5;
      } else this.history = view;
      this.season = season;
      this.raceId = raceId;
      if (!view.current) {
        const task = view.load(client);
        this.requestUpdate();
        await task;
        if (epoch !== this.epoch) return;
        // Ask a cooperating card on this socket/entry to release one hidden,
        // idle selection, then make one paced retry of the submitted choice.
        if (errorCode(view.error) === "snapshot_limit") {
          if (await releaseUnusedSnapshot(client)) {
            if (epoch === this.epoch) await view.load(client);
          }
        }
      }
      if (epoch === this.epoch) this.requestUpdate();
    } catch (error) {
      if (epoch === this.epoch) this.formError = error;
    } finally {
      this.submitting = false;
      this.requestUpdate();
    }
  }
  private async discardSnapshot(key: string, view: PageView) {
    this.snapshots.delete(key);
    if (this.history === view) this.history = undefined;
    if (this.analytics === view) this.analytics = undefined;
    await view.invalidate();
  }
  private state(title: string, message: string, loading = false) {
    return html`<div class=${`state${loading ? " loading" : ""}`} role="status">
      <h3>${title}</h3>
      <p class="muted">${message}</p>
    </div>`;
  }
  private errorView(error: unknown, retry?: () => void) {
    const calm = [
      "no_active_session",
      "no_records",
      "not_reported",
      "unavailable",
      "snapshot_expired",
      "snapshot_invalid",
      "snapshot_changed",
      "snapshot_limit",
    ].includes(errorCode(error));
    return html`<div
      class=${calm ? "state" : "state error"}
      role=${calm ? "status" : "alert"}
    >
      <h3>${calm ? "Selection unavailable" : "Unable to load this view"}</h3>
      <p>${errorMessage(error)}</p>
      ${retry
        ? html`<div><button @click=${retry}>Retry / reconnect</button></div>`
        : nothing}
    </div>`;
  }
  private badge(text: string, tone = "neutral", raceFlag = false) {
    return html`<span class=${`badge ${tone}${raceFlag ? " race-flag" : ""}`}
      >${text}</span
    >`;
  }
  private pager(view: PageView) {
    const p = view.current?.pagination;
    return html`${view.expired
        ? html`<p class="notice">
            Snapshot expired; these are cached historical observations. Restart
            to request a fresh selection.
          </p>`
        : nothing}${view.error
        ? this.errorView(view.error, () => void this.page(view, "retry"))
        : nothing}
      <div class="pager">
        <small
          >${p
            ? `Records ${p.returned ? p.offset + 1 : 0}–${p.offset + p.returned} of ${this.formatNumber(p.total)} · ${view.records.length} retained in this view`
            : "No records loaded"}${view.loading ? " · Loading…" : ""}</small
        >
        <div class="actions">
          ${view.pages.size > 1
            ? html`<label class="field"
                >Loaded page<select
                  aria-label="Return to loaded page"
                  .value=${String(p?.offset ?? 0)}
                  ?disabled=${view.loading || view.expired}
                  @change=${async (e: Event) => {
                    if (!this.client) return;
                    await view.jump(
                      this.client,
                      Number((e.target as HTMLSelectElement).value),
                    );
                    this.requestUpdate();
                  }}
                >
                  ${[...view.pages.values()]
                    .sort((a, b) => a.pagination.offset - b.pagination.offset)
                    .map(
                      (page) =>
                        html`<option value=${page.pagination.offset}>
                          ${this.formatNumber(
                            page.pagination.offset + 1,
                          )}–${this.formatNumber(
                            page.pagination.offset + page.pagination.returned,
                          )}
                        </option>`,
                    )}
                </select></label
              >`
            : nothing}
          <button
            ?disabled=${view.loading || !view.canPrevious}
            @click=${() => void this.page(view, "previous")}
          >
            Previous</button
          ><button
            ?disabled=${view.loading || p?.next_offset == null}
            @click=${() => void this.page(view, "next")}
          >
            Next page</button
          >${view.error || view.expired
            ? html`<button
                ?disabled=${view.loading}
                @click=${() => void this.page(view, "restart")}
              >
                Restart selection
              </button>`
            : nothing}
        </div>
      </div>`;
  }
  private renderOverview() {
    const b = this.bootstrapData!,
      live = this.liveData;
    const session = live?.session;
    const race = session
      ? this.currentRace
      : b.upcoming.find((r) => r.series_id === this.series);
    const weekend = b.upcoming.find((r) => r.series_id === this.series);
    const nextInstant = [
      race?.start_time,
      ...(race?.sessions ?? []).map((s) => s.start_time),
    ]
      .filter(
        (s): s is string =>
          !!s && instant(s) !== null && instant(s)! > Date.now(),
      )
      .sort((a, b) => instant(a)! - instant(b)!)[0];
    const health = freshness(live),
      raceFlag = flag(live);
    const leader = live?.leaderboard?.find(
      (d) => d.driver_id === live.leader_driver_id,
    );
    const remaining = countdown(nextInstant);
    const favorites = live?.leaderboard?.filter((d) => d.favorite) ?? [];
    return html`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">Your race day, in focus</p>
          <h2>Race Center</h2>
        </div>
        ${this.badge(health.text, health.tone)}
      </div>
      <section class="panel hero">
        <div class="hero-content">
          <p class="eyebrow">
            ${SERIES[this.series]} ·
            ${session
              ? "Reported session"
              : race
                ? "Next known event"
                : "Schedule & live coverage"}
          </p>
          <h3 class="race-title">
            ${session?.run_name ??
            race?.name ??
            "Waiting for the next green flag."}
          </h3>
          <p class="hero-track">
            ${race?.track ?? "Track not reported"}${race?.season
              ? ` · ${race.season}`
              : ""}
          </p>
          <div class="actions">
            ${session
              ? this.badge(raceFlag.text, raceFlag.tone, true)
              : this.badge(race?.status ?? "No active session")}${session
              ? this.badge(
                  `${label(session.status)} · ${label(session.progress)}`,
                )
              : nothing}
          </div>
          <div class="actions">
            <button
              class="primary"
              @click=${() => this.navigate("Live Timing")}
            >
              Open live timing ↗</button
            ><button @click=${() => this.navigate("Race Weekend")}>
              Race weekend
            </button>
          </div>
        </div>
        <div class="hero-side">
          ${session
            ? html`<div>
                  <p class="eyebrow">Reported lap</p>
                  <p class="lap-count">
                    ${this.formatNumber(session.lap)}
                    <span>/ ${this.formatNumber(session.total_laps)}</span>
                  </p>
                </div>
                ${session.lap !== null &&
                session.total_laps !== null &&
                session.total_laps > 0
                  ? html`<div
                      class="progress"
                      role="meter"
                      aria-label="Reported session laps"
                      aria-valuemin="0"
                      aria-valuemax=${session.total_laps}
                      aria-valuenow=${Math.min(session.lap, session.total_laps)}
                    >
                      <div
                        style=${`width:${Math.max(0, Math.min(100, (session.lap / session.total_laps) * 100))}%`}
                      ></div>
                    </div>`
                  : nothing}
                <p>
                  <small>Leading the reported field</small><br /><strong
                    >${leader?.name ?? "Leader unavailable"}</strong
                  >
                </p>`
            : html`<div>
                  <p class="eyebrow">
                    ${remaining ? "Starts in" : "Event time"}
                  </p>
                  <p class="lap-count">${remaining ?? "—"}</p>
                </div>
                <p>
                  ${date(nextInstant, this.hass)}<br /><small
                    >${remaining
                      ? "Known future instant"
                      : "No reliable future instant available"}</small
                  >
                </p>`}
        </div>
      </section>
      <div class="stat-grid">
        <div class="stat">
          <span>Reported entries</span
          ><strong>${this.formatNumber(live?.reported_count)}</strong>
        </div>
        <div class="stat">
          <span>Laps remaining</span
          ><strong>${this.formatNumber(session?.laps_remaining)}</strong>
        </div>
        <div class="stat">
          <span>Stage observation</span
          ><strong>${this.formatNumber(session?.stage?.number)}</strong>
        </div>
      </div>
      <div class="two-col">
        <section class="stack">
          <div class="row">
            <h3>Following the field</h3>
            <small>Integration favorites</small>
          </div>
          ${favorites.length
            ? html`<div class="favorite-grid">
                ${favorites.map(
                  (d) =>
                    html`<button
                      class="panel favorite"
                      @click=${(e: Event) => void this.openDriver(d, e)}
                    >
                      <span class="row"
                        ><span class="car">${d.car_number ?? "—"}</span
                        ><span class="position"
                          >P${this.formatNumber(d.position)}</span
                        ></span
                      ><strong>${d.name ?? `Driver ${d.driver_id}`}</strong
                      ><small
                        >★ Favorite ·
                        ${d.running_status ?? "Status unknown"}</small
                      >
                    </button>`,
                )}
              </div>`
            : html`<div class="panel">
                <p>
                  ${b.favorite_driver_ids.length
                    ? "Favorite timing is unavailable for this series."
                    : "Choose favorite drivers in the integration options."}
                </p>
                ${b.references.drivers.map(
                  (d) =>
                    html`<p class="muted">★ ${d.name} · ${d.driver_id}</p>`,
                )}
              </div>`}
        </section>
        <section class="panel stack">
          <h3>${session ? "Next known weekend" : "Weekend notebook"}</h3>
          ${weekend?.sessions?.length
            ? weekend.sessions.map(
                (s) =>
                  html`<div>
                    <p>${s.name} <small>· ${label(s.kind)}</small></p>
                    <small>${date(s.start_time, this.hass)}</small>
                  </div>`,
              )
            : html`<p class="muted">
                ${weekend
                  ? "Session times are not confirmed."
                  : "No scheduled future event in the retained catalog. Open Race Weekend for retained events or use an explicit historical race key."}
              </p>`}<button
            class="quiet"
            @click=${() => this.navigate("History")}
          >
            Explore race history →
          </button>
        </section>
      </div>
      ${live?.leaderboard?.length
        ? html`<section class="panel overview-field">
            <div class="row">
              <h3>${messages.front}</h3>
              <button @click=${() => this.navigate("Live Timing")}>
                Full timing tower →
              </button>
            </div>
            <div class="front-grid">
              ${live.leaderboard
                .slice()
                .sort(
                  (a, b) => (a.position ?? Infinity) - (b.position ?? Infinity),
                )
                .slice(0, 5)
                .map(
                  (d) =>
                    html`<button
                      @click=${(e: Event) => void this.openDriver(d, e)}
                    >
                      <span class="muted"
                        >P${this.formatNumber(d.position)}</span
                      ><span class="car">${d.car_number ?? "—"}</span
                      ><strong
                        >${d.favorite ? "★ " : ""}${d.name ??
                        `Driver ${d.driver_id}`}</strong
                      >
                    </button>`,
                )}
            </div>
          </section>`
        : nothing}
      ${!session
        ? this.state(
            "Session coverage",
            live
              ? `${label(live.availability)}. Timing appears only when the source supplies fresh matching observations.`
              : "Waiting for the first live source snapshot.",
            !live,
          )
        : nothing}${this.renderDetail()}
    </div>`;
  }
  private renderTiming() {
    const live = this.liveData,
      session = live?.session,
      health = freshness(live),
      raceFlag = flag(live);
    return html`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">${SERIES[this.series]} · Timing tower</p>
          <h2>${session?.run_name ?? "Live Timing"}</h2>
          <p class="muted">
            ${label(session?.status)}${session
              ? ` · Reported lap ${this.formatNumber(session.lap)} / ${this.formatNumber(session.total_laps)}`
              : ""}
          </p>
        </div>
        <div class="actions">
          ${this.badge(health.text, health.tone)}${session
            ? this.badge(raceFlag.text, raceFlag.tone, true)
            : nothing}
        </div>
      </div>
      ${live?.leaderboard?.length
        ? html`<nrc-leaderboard
            .rows=${live.leaderboard}
            .hass=${this.hass}
            .compact=${this.compact}
            @driver-open=${(e: CustomEvent<Driver>) =>
              void this.openDriver(e.detail, e)}
          ></nrc-leaderboard>`
        : this.state(
            live ? "No current timing" : "Connecting to the timing feed",
            live
              ? `${label(live.availability)}. Fresh matching observations are required; stale results are withheld.`
              : "Waiting for an authenticated live snapshot.",
            !live,
          )}${session?.stage
        ? html`<div class="notice">
            Reported stage ${this.formatNumber(session.stage.number)} · finish
            at lap ${this.formatNumber(session.stage.finish_at_lap)} · stage
            laps ${this.formatNumber(session.stage.laps_in_stage)}. Provisional
            observations.
          </div>`
        : nothing}${live
        ? html`<section class="panel stack">
            <h3>Associated scoring observations</h3>
            <div class="actions">
              ${(["pits", "stages", "points"] as const).map(
                (k) =>
                  html`<button @click=${() => void this.loadDetail(k, true)}>
                    ${label(k)} · ${label(live.scoring[k]?.status)}
                  </button>`,
              )}
            </div>
            <p class="muted">
              <small
                >Only supported associations are shown. No championship or
                strategy conclusions.</small
              >
            </p>
          </section>`
        : nothing}${live?.omitted_count
        ? html`<p class="notice">
            Source normalizer omitted ${live.omitted_count} entries. This is not
            a complete official entry list.
          </p>`
        : nothing}${this.renderDetail()}
    </div>`;
  }
  private renderDetail() {
    const d = this.detailDriver,
      v = this.detail;
    if (!d && !v && !this.detailError && !this.detailEmpty) return nothing;
    return html`<section
      class="panel stack detail-panel"
      aria-label="Driver and scoring details"
      @keydown=${(e: KeyboardEvent) => {
        if (e.key === "Escape") this.closeDetail();
      }}
    >
      <div class="row">
        <h3>
          ${d
            ? `${d.name ?? d.driver_id} · #${d.car_number ?? "—"}`
            : `${label(v?.selection.collection)} observations`}
        </h3>
        <button class="detail-close" @click=${() => this.closeDetail()}>
          Close
        </button>
      </div>
      ${d
        ? html`<div class="stat-grid">
              <div class="stat">
                <span>Position</span
                ><strong>${this.formatNumber(d.position)}</strong>
              </div>
              <div class="stat">
                <span>Best lap*</span
                ><strong
                  >${this.formatNumber(d.best_lap_time, undefined, 3)}</strong
                >
              </div>
              <div class="stat">
                <span>Laps</span
                ><strong>${this.formatNumber(d.laps_completed)}</strong>
              </div>
            </div>
            <p class="muted">
              <small
                >* Source unit unverified. Pit stops and laps-led intervals
                retain reported boundaries.</small
              >
            </p>
            <div class="actions">
              <button @click=${() => void this.loadDetail("pit_stops")}>
                Load pit observations</button
              ><button @click=${() => void this.loadDetail("laps_led")}>
                Load laps-led intervals
              </button>
            </div>
            <details>
              <summary>Reported driver measurements</summary>
              ${values(d, 0, numberLocale(this.hass))}
            </details>`
        : nothing}${this.detailEmpty
        ? this.state("No live observations", this.detailEmpty)
        : nothing}${this.detailError
        ? this.errorView(this.detailError)
        : nothing}${v
        ? html`${v.current
            ? html`<p class="muted">
                  ${label(v.current.availability)} · ${label(v.current.reason)}
                  · Race ${v.current.identity?.race_id ?? "Unknown"} / timing
                  run ${v.current.identity?.run_id ?? "Unknown"}
                </p>
                ${v.current.provenance
                  ? html`<details>
                      <summary>Source provenance</summary>
                      ${values(
                        v.current.provenance,
                        0,
                        numberLocale(this.hass),
                      )}
                    </details>`
                  : nothing}
                <p class="notice">
                  Provisional reported observations. Source timing units remain
                  unverified.
                </p>
                ${v.current.records.length
                  ? records(v.current.records, this.hass)
                  : this.state(
                      "No detail records",
                      "This source has no supported records for the selected collection.",
                    )}`
            : v.loading
              ? this.state(
                  "Loading observations",
                  "Requesting only the selected detail collection.",
                  true,
                )
              : nothing}${this.pager(v)}`
        : nothing}
    </section>`;
  }
  private renderWeekend() {
    const view = this.schedules.get(this.series);
    const rows = view?.current?.records ?? [];
    const races = rows.filter((r) => r.kind === "race");
    const sessions = rows.filter((r) => r.kind === "session");
    return html`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">${SERIES[this.series]} · Retained schedule</p>
          <h2>Race Weekend</h2>
          <p class="muted">
            Known events and sessions ·
            ${this.hass?.config?.time_zone ?? "browser local time"}
          </p>
        </div>
        ${this.badge(
          this.bootstrapData?.source_state.find(
            (s) => s.series_id === this.series,
          )?.schedule ?? "unknown",
        )}
      </div>
      ${this.bootstrapData?.navigation.find((n) => n.series_id === this.series)
        ?.failed_seasons.length
        ? html`<p class="notice">
            Some retained seasons are unavailable. Available peers do not
            establish full schedule coverage.
          </p>`
        : nothing}
      <div class="schedule">
        ${races.map((row) => {
          const r = row.value!;
          const track = this.bootstrapData?.references.tracks.find(
            (t) => t.track_id === r.track_id,
          );
          return html`<article class="panel event-card">
            <div class="event-number">${r.season ?? "—"}</div>
            <div>
              <p class="eyebrow">${r.track ?? "Track unknown"}</p>
              <h3>${r.name}</h3>
              <p class="muted">
                ${date(r.start_time, this.hass)} · ${label(r.status)}
              </p>
              ${track
                ? html`<small
                    >${track.city ?? ""}${track.state ? `, ${track.state}` : ""}
                    · ${label(track.track_type)} ·
                    ${this.formatNumber(track.length_miles, undefined, 2)}
                    reported miles</small
                  >`
                : nothing}
              <div class="sessions">
                ${sessions
                  .filter(
                    (s) => s.race_id === r.race_id && s.season === r.season,
                  )
                  .map((s) => {
                    const v = s.value!;
                    return "session_id" in v
                      ? html`<div class="session-row">
                          <span
                            >${v.name} <small>· ${label(v.kind)}</small></span
                          ><span
                            >${date(v.start_time, this.hass)}<small>
                              · ${label(v.status)}</small
                            ></span
                          >
                        </div>`
                      : nothing;
                  })}
              </div>
              ${r.sessions_failed
                ? html`<p class="notice">
                    Session enrichment unavailable; race schedule retained.
                  </p>`
                : nothing}
            </div>
            <div class="actions">
              <button
                ?disabled=${r.season === null}
                @click=${() => {
                  if (r.season) {
                    this.season = r.season;
                    this.raceId = r.race_id;
                    this.history = undefined;
                    this.navigate("History");
                  }
                }}
              >
                Select race →
              </button>
            </div>
          </article>`;
        })}${sessions.filter(
          (s) =>
            !races.some(
              (r) =>
                r.value?.race_id === s.race_id && r.value?.season === s.season,
            ),
        ).length
          ? html`<p class="notice">
                This page continues the preceding race's sessions. Parent race
                IDs are retained below.
              </p>
              ${records(
                sessions.filter(
                  (s) =>
                    !races.some(
                      (r) =>
                        r.value?.race_id === s.race_id &&
                        r.value?.season === s.season,
                    ),
                ),
              )}`
          : nothing}${!rows.length
          ? this.state(
              view?.loading ? "Loading retained events" : "No scheduled events",
              view?.loading
                ? "Reading the integration’s retained schedule catalog."
                : "The retained catalog contains no events for this series. Historical lookup remains available.",
              view?.loading,
            )
          : nothing}
      </div>
      ${view ? this.pager(view) : nothing}
    </div>`;
  }
  private renderForm(analytics: boolean) {
    const nav = this.bootstrapData?.navigation.find(
      (n) => n.series_id === this.series,
    );
    const selected = analytics
      ? this.analytics?.selection
      : this.history?.selection;
    const datasets =
      selected?.datasets ?? (analytics ? ["laps", "weekend"] : ["weekend"]);
    const retained = [...(this.schedules.get(this.series)?.records ?? [])]
      .filter((r) => r.kind === "race")
      .map((r) => r.value!)
      .concat(
        this.bootstrapData?.upcoming.filter(
          (r) => r.series_id === this.series,
        ) ?? [],
      )
      .filter(
        (r, i, all) =>
          all.findIndex(
            (x) => x.race_id === r.race_id && x.season === r.season,
          ) === i,
      );
    return html`<form
      class="panel stack"
      @submit=${(e: SubmitEvent) => void this.submit(e, analytics)}
    >
      <div class="filters">
        <label class="field"
          >Series<select
            aria-label="Historical series"
            .value=${String(this.series)}
            @change=${(e: Event) =>
              this.selectSeries(Number((e.target as HTMLSelectElement).value))}
          >
            ${this.bootstrapData!.series_ids.map(
              (s) => html`<option value=${s}>${SERIES[s]}</option>`,
            )}
          </select></label
        ><label class="field"
          >Season<input
            name="season"
            type="number"
            required
            min="1948"
            max="9999"
            .value=${String(selected?.season ?? this.season)}
            list="retained-seasons" /></label
        ><datalist id="retained-seasons">
          ${nav?.seasons.map((s) => html`<option value=${s}></option>`)}</datalist
        ><label class="field wide"
          >Known retained race<select
            @change=${(e: Event) => {
              const [season, race] = (
                e.target as HTMLSelectElement
              ).value.split(":");
              if (race) {
                this.season = Number(season);
                this.raceId = race;
                const form = (e.target as HTMLElement).closest("form")!;
                (form.elements.namedItem("season") as HTMLInputElement).value =
                  season;
                (form.elements.namedItem("race") as HTMLInputElement).value =
                  race;
              }
            }}
          >
            <option value="">
              Choose a retained race or enter a key below
            </option>
            ${retained.map(
              (r) =>
                html`<option value=${`${r.season}:${r.race_id}`}>
                  ${r.season ?? "?"} · ${r.name} · ${r.race_id}
                </option>`,
            )}
          </select></label
        ><label class="field"
          >Race ID · manual key<input
            name="race"
            required
            inputmode="numeric"
            pattern="[0-9]+"
            .value=${String(selected?.race_id ?? this.raceId)}
            placeholder="e.g. 88001"
        /></label>
      </div>
      <div class="filters">
        <fieldset>
          <legend>Explicit datasets</legend>
          ${DATASETS.map(
            (d) =>
              html`<label class="check"
                ><input
                  type="checkbox"
                  name="dataset"
                  value=${d}
                  .checked=${datasets.includes(d)}
                />
                ${label(d)}</label
              >`,
          )}
        </fieldset>
      </div>
      ${analytics
        ? html`<div class="filters">
              <label class="field wide"
                >NASCAR driver IDs · comma separated, 1–8<input
                  name="drivers"
                  required
                  .value=${selected?.driver_ids?.join(", ") ??
                  this.bootstrapData!.favorite_driver_ids.slice(0, 2).join(
                    ", ",
                  )}
                  placeholder="99002, 99003" /></label
              ><label class="field"
                >First lap<input
                  type="number"
                  name="first"
                  min="0"
                  max="10000000000"
                  required
                  .value=${String(selected?.first_lap ?? 1)} /></label
              ><label class="field"
                >Last lap<input
                  type="number"
                  name="last"
                  min="0"
                  max="10000000000"
                  required
                  .value=${String(selected?.last_lap ?? 100)} /></label
              ><label class="field wide"
                >Comparison time basis<select
                  name="basis"
                  .value=${selected?.time_basis ?? "all_available"}
                >
                  <option value="all_available">
                    All available valid laps per driver
                  </option>
                  <option value="overlapping_valid_laps">
                    Overlapping valid laps across selected drivers
                  </option>
                </select></label
              >
              <fieldset>
                <legend>Consecutive lap windows</legend>
                ${[5, 10, 15, 20, 25, 30].map(
                  (w) =>
                    html`<label class="check"
                      ><input
                        name="window"
                        type="checkbox"
                        value=${w}
                        .checked=${(selected?.windows ?? [5]).includes(w)}
                      />${w}</label
                    >`,
                )}
              </fieldset>
            </div>
            <p class="muted">
              <small
                >Up to 5,000 lap numbers; drivers × lap span × window count ≤
                60,000. Missing data is preserved. Select loop, averages or
                stages to include supported reported statistics.</small
              >
            </p>`
        : nothing}
      <p class="muted">
        <small
          >Manual keys permit valid selections outside the retained schedule;
          endpoint coverage is unverified across seasons. Datasets are requested
          only on submission. Recent selections are retained for reuse; older
          selections are released as you explore.</small
        >
      </p>
      <div>
        <button
          class="primary"
          type="submit"
          ?disabled=${this.submitting ||
          (analytics ? this.analytics : this.history)?.loading}
        >
          ${analytics ? "Analyze selection" : "Load race records"}
        </button>
      </div>
      ${this.formError ? this.errorView(this.formError) : nothing}
    </form>`;
  }
  private retainedSelections() {
    return this.snapshots.size
      ? html`<details class="selection-library">
          <summary>${messages.retained}</summary>
          <div class="actions">
            ${[...this.snapshots.values()].map(
              (v) =>
                html`<button
                  @click=${() => {
                    this.formError = undefined;
                    this.selectSeries(v.selection.series_id);
                    this.season = v.selection.season!;
                    this.raceId = String(v.selection.race_id);
                    if (v.command === "history") this.history = v;
                    else {
                      this.analytics = v;
                      if (!v.selection.windows?.includes(this.chartWindow))
                        this.chartWindow = v.selection.windows?.[0] ?? 5;
                    }
                    this.navigate(
                      v.command === "history" ? "History" : "Analytics",
                    );
                    this.requestUpdate();
                  }}
                >
                  ${v.command === "history" ? "History" : "Analytics"} ·
                  ${SERIES[v.selection.series_id]} · ${v.selection.season} /
                  ${v.selection.race_id}${v.expired ? " · expired" : ""}
                </button>`,
            )}
          </div>
          <p class="muted"><small>${messages.snapshotHint}</small></p>
        </details>`
      : nothing;
  }
  private renderHistory() {
    const view = this.history,
      page = view?.current,
      kind = page?.records.some((r) => r.kind === this.historyKind)
        ? this.historyKind
        : "all";
    return html`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">The race archive</p>
          <h2>History</h2>
          <p class="muted">
            Reported results, session records and source observations.
          </p>
        </div>
      </div>
      ${this.retainedSelections()}${this.renderForm(false)}${page
        ? html`<div class="section-head">
              <h3>
                ${page.records.find((r) => r.kind === "weekend")?.value?.name ??
                `Race ${page.race?.race_id ?? this.raceId}`}
              </h3>
              ${this.badge(label(page.status))}
            </div>
            ${evidence(page, this.hass)}${this.pager(view!)}${resultTable(
              page.records,
              this.hass,
            )}${page.records.length
              ? html`<label class="field"
                    >${messages.records}<select
                      aria-label=${messages.records}
                      .value=${kind}
                      @change=${(e: Event) => {
                        this.historyKind = (
                          e.target as HTMLSelectElement
                        ).value;
                        this.requestUpdate();
                      }}
                    >
                      <option value="all">All supported record types</option>
                      ${[...new Set(page.records.map((r) => r.kind))].map(
                        (kind) =>
                          html`<option value=${kind}>${label(kind)}</option>`,
                      )}
                    </select></label
                  >
                  <details ?open=${kind !== "all"}>
                    <summary>
                      Explore ${page.records.length} records on this page ·
                      metadata, stages, laps, notes & pits
                    </summary>
                    ${records(
                      page.records.filter(
                        (r) => kind === "all" || r.kind === kind,
                      ),
                      this.hass,
                    )}
                  </details>`
              : this.state(
                  "No historical records",
                  "This selection returned no records. Review dataset availability above.",
                )}`
        : view?.loading
          ? this.state(
              "Loading historical selection",
              "Building one immutable snapshot for the explicitly selected datasets.",
              true,
            )
          : this.state(
              "Choose a race to begin",
              "Select a season and retained race, or enter a valid manual race key.",
            )}${view && !page ? this.pager(view) : nothing}
    </div>`;
  }
  private renderAnalytics() {
    const view = this.analytics,
      page = view?.current;
    const all = view?.records ?? [];
    const chartRows =
      this.chartMode === "window"
        ? all.filter((r) => r.kind !== "window" || r.size === this.chartWindow)
        : all;
    return html`<div class="stack">
      <div class="section-head">
        <div>
          <p class="eyebrow">Understand the observations</p>
          <h2>Analytics</h2>
          <p class="muted">
            Interactive comparisons from Phase 4B analytics · no inferred
            strategy.
          </p>
        </div>
      </div>
      ${this.retainedSelections()}${this.renderForm(true)}${page
        ? html`<div class="row">
              <h3>
                Selected race ${page.query?.key.race_id ?? "—"} · laps
                ${page.query?.first_lap ?? "—"}–${page.query?.last_lap ?? "—"}
              </h3>
              ${this.badge(label(page.status))}
            </div>
            <p class="notice">
              ${label(page.query?.time_basis)} · ${label(page.reason)}. Charts
              and summaries contain loaded pages only. Continue paging for later
              drivers, comparisons and reported performance; retention is
              bounded to 1,600 records.
            </p>
            ${evidence(page, this.hass)}${this.pager(view!)}
            <p class="notice" role="status">
              Loaded record ranges:
              ${[...view!.pages.values()]
                .sort((a, b) => a.pagination.offset - b.pagination.offset)
                .map(
                  (p) =>
                    `${this.formatNumber(p.pagination.offset + 1)}–${this.formatNumber(p.pagination.offset + p.pagination.returned)}`,
                )
                .join(", ")}
              of ${this.formatNumber(page.pagination.total)}. These ranges
              include headers and metrics, not only lap samples.
            </p>
            <div class="filters">
              <label class="field"
                >Chart<select
                  .value=${this.chartMode}
                  @change=${(e: Event) => {
                    this.chartMode = (e.target as HTMLSelectElement)
                      .value as ChartMode;
                    this.requestUpdate();
                  }}
                >
                  <option value="time">Lap-time progression</option>
                  <option value="position">Position progression</option>
                  <option value="delta">Consecutive-lap change</option>
                  <option
                    value="window"
                    ?disabled=${!page.query?.windows.length}
                  >
                    Consecutive-window mean
                  </option>
                </select></label
              >${this.chartMode === "window"
                ? html`<label class="field"
                    >Window<select
                      .value=${String(this.chartWindow)}
                      @change=${(e: Event) => {
                        this.chartWindow = Number(
                          (e.target as HTMLSelectElement).value,
                        );
                        this.requestUpdate();
                      }}
                    >
                      ${page.query?.windows.map(
                        (w) => html`<option value=${w}>${w} laps</option>`,
                      )}
                    </select></label
                  >`
                : nothing}
            </div>
            <nrc-chart
              .rows=${chartRows}
              .mode=${this.chartMode}
              .locale=${numberLocale(this.hass)}
            ></nrc-chart>
            <nrc-metric-chart
              .rows=${all}
              .locale=${numberLocale(this.hass)}
            ></nrc-metric-chart>
            ${all
              .filter((r) => r.kind === "driver")
              .map(
                (r) =>
                  html`<section class="stack">
                    <h3>
                      Driver ${r.driver_id} · ${label(r.value?.status)} ·
                      fastest recorded lap
                      ${this.formatNumber(r.value?.fastest_lap)}
                    </h3>
                    <div class="metric-grid">
                      ${r.value?.metrics.map((m) =>
                        metricCard(m, numberLocale(this.hass)),
                      )}
                    </div>
                    <details>
                      <summary>Coverage and exclusions</summary>
                      ${values(r.value?.coverage, 0, numberLocale(this.hass))}
                      <p>${label(r.value?.reason)}</p>
                    </details>
                  </section>`,
              )}${page.race_metrics?.length
              ? html`<div class="metric-grid">
                  ${page.race_metrics.map((m) =>
                    metricCard(m, numberLocale(this.hass)),
                  )}
                </div>`
              : nothing}
            <details>
              <summary>
                Comparisons, consecutive windows & reported performance ·
                current page
              </summary>
              ${records(
                page.records.filter((r) => r.kind !== "samples"),
                this.hass,
              )}
            </details>
            <details>
              <summary>Analytics caveats</summary>
              ${page.caveats?.map((c) => html`<p>${label(c)}</p>`)}
            </details>`
        : view?.loading
          ? this.state(
              "Calculating selected observations",
              "The backend applies the existing analytics contract and computation limits.",
              true,
            )
          : this.state(
              "Build a comparison",
              "Choose drivers, lap range, datasets and a supported window.",
            )}${view && !page ? this.pager(view) : nothing}
    </div>`;
  }
  render() {
    const b = this.bootstrapData,
      health = freshness(this.liveData);
    return html`<ha-card ?data-compact=${this.compact}
      ><header class="masthead">
        <div class="brand">
          <span class="brand-mark" aria-hidden="true"
            ><i></i><i></i><i></i
          ></span>
          <div>
            <h1 class="brand-title">
              ${this.config.title ?? "NASCAR Race Center"}
            </h1>
            <p class="eyebrow">Race intelligence · Home Assistant</p>
          </div>
        </div>
        ${b
          ? html`<div class="tools">
              <label class="series-label"
                ><span class="eyebrow">${messages.density}</span
                ><select
                  aria-label=${messages.density}
                  .value=${this.compact ? "compact" : "comfortable"}
                  @change=${(e: Event) => {
                    this.compact =
                      (e.target as HTMLSelectElement).value === "compact";
                    this.requestUpdate();
                  }}
                >
                  <option value="comfortable">${messages.comfortable}</option>
                  <option value="compact">${messages.compact}</option>
                </select></label
              >
              <label class="series-label"
                ><span class="eyebrow">Series</span
                ><select
                  aria-label="Selected series"
                  .value=${String(this.series)}
                  @change=${(e: Event) =>
                    this.selectSeries(
                      Number((e.target as HTMLSelectElement).value),
                    )}
                >
                  ${b.series_ids.map(
                    (s) => html`<option value=${s}>${SERIES[s]}</option>`,
                  )}
                </select></label
              >
            </div>`
          : nothing}
      </header>
      ${b?.provider === "demo"
        ? html`<div class="demo" role="note">
            DEMONSTRATION · Simulated races & drivers · not genuine NASCAR
            results · offline provider
          </div>`
        : nothing}${b
        ? html`<nav class="nav" aria-label="Race Center sections">
            ${SECTIONS.map(
              (s) =>
                html`<button
                  aria-current=${s === this.section ? "page" : nothing}
                  @click=${() => this.navigate(s)}
                >
                  ${s}
                </button>`,
            )}
          </nav>`
        : nothing}
      <main
        @keydown=${(e: KeyboardEvent) => {
          if (e.key === "Escape" && (this.detailDriver || this.detail))
            this.closeDetail();
        }}
        aria-busy=${this.loading ? "true" : "false"}
      >
        ${this.loading
          ? this.state(
              "Preparing your Race Center",
              "Connecting through Home Assistant’s authenticated WebSocket API.",
              true,
            )
          : nothing}${this.error
          ? this.errorView(this.error, () => this.scheduleStart())
          : nothing}${!this.config.entry_id && !this.loading && !this.error
          ? html`<div class="state">
              <h2>Select an integration entry</h2>
              <p>
                Dashboard API v1 requires administrator access. Choose a loaded
                entry or set <code>entry_id</code> in the card editor. The card
                never infers entries from entity names.
              </p>
              <label class="field"
                >NASCAR Race Center entry<select
                  @change=${(e: Event) => {
                    const value = (e.target as HTMLSelectElement).value;
                    if (value) this.chooseEntry(value);
                  }}
                >
                  <option value="">Select an entry</option>
                  ${this.entries.map(
                    (e) =>
                      html`<option
                        ?disabled=${e.state !== "loaded"}
                        value=${e.entry_id}
                      >
                        ${e.title} · ${e.state}
                      </option>`,
                  )}
                </select></label
              >${!this.entries.length
                ? html`<p class="muted">
                    No entries found. Add the NASCAR Race Center integration,
                    then reconnect.
                  </p>`
                : nothing}
            </div>`
          : nothing}${b
          ? this.section === "Race Center"
            ? this.renderOverview()
            : this.section === "Live Timing"
              ? this.renderTiming()
              : this.section === "Race Weekend"
                ? this.renderWeekend()
                : this.section === "History"
                  ? this.renderHistory()
                  : this.renderAnalytics()
          : nothing}
      </main>
      <footer class="source">
        <span
          >${b
            ? `${b.provider === "demo" ? "Simulated" : "Experimental"} source · ${label(this.section === "History" || this.section === "Analytics" ? "on_demand_snapshot" : health.text)}`
            : "Authenticated dashboard API v1"}</span
        ><span
          >Content updated:
          ${date(this.liveData?.source_updated_at, this.hass)}</span
        ><span>Card ${VERSION} · API v1</span>
      </footer></ha-card
    >`;
  }
}
customElements.define("nascar-race-center-card", NascarRaceCenterCard);
const registry = window as unknown as {
  customCards?: {
    type: string;
    name: string;
    description: string;
    preview: boolean;
  }[];
};
registry.customCards ??= [];
if (!registry.customCards.some((c) => c.type === "nascar-race-center-card"))
  registry.customCards.push({
    type: "nascar-race-center-card",
    name: "NASCAR Race Center",
    description:
      "Five racing views with authenticated dashboard API v1. Administrator access required.",
    preview: true,
  });
