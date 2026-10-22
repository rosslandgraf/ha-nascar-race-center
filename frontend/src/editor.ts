import { defineOnce } from "./register";
import { LitElement, html } from "lit";
import type { CardConfig, Entry, Hass } from "./types";
import { discoverEntries, errorMessage } from "./api";
import { SECTIONS, SERIES } from "./types";
import { styles } from "./styles";
export class CardEditor extends LitElement {
  static properties = {
    config: { state: true },
    entries: { state: true },
    error: { state: true },
  };
  static styles = styles;
  config: CardConfig = { type: "custom:nascar-race-center-card" };
  entries: Entry[] = [];
  error?: unknown;
  private hostHass?: Hass;
  private generation = 0;
  set hass(hass: Hass | undefined) {
    if (!hass) return;
    const changed = this.hostHass?.connection !== hass.connection;
    this.hostHass = hass;
    if (changed && this.isConnected) void this.discover();
  }
  get hass() {
    return this.hostHass;
  }
  setConfig(config: CardConfig) {
    this.config = { ...config };
  }
  connectedCallback() {
    super.connectedCallback();
    if (this.hostHass) void this.discover();
  }
  disconnectedCallback() {
    super.disconnectedCallback();
    this.generation++;
  }
  private async discover() {
    const gen = ++this.generation;
    try {
      const entries = await discoverEntries(this.hostHass!);
      if (gen === this.generation) {
        this.entries = entries;
        this.error = undefined;
      }
    } catch (error) {
      if (gen === this.generation) this.error = error;
    }
  }
  private change(key: keyof CardConfig, value: unknown) {
    const next = { ...this.config, [key]: value || undefined };
    this.config = next;
    this.dispatchEvent(
      new CustomEvent("config-changed", {
        detail: { config: next },
        bubbles: true,
        composed: true,
      }),
    );
  }
  render() {
    return html`<div class="stack">
      <p>
        Dashboard API v1 requires a Home Assistant administrator. Select the
        integration entry explicitly; favorites and series are managed by the
        integration.
      </p>
      ${this.error
        ? html`<p role="alert">${errorMessage(this.error)}</p>`
        : ""}<label class="field"
        >Integration entry<select
          .value=${this.config.entry_id ?? ""}
          @change=${(e: Event) =>
            this.change("entry_id", (e.target as HTMLSelectElement).value)}
        >
          <option value="">Select a NASCAR Race Center entry</option>
          ${this.entries.map(
            (e) =>
              html`<option value=${e.entry_id}>
                ${e.title} · ${e.state}
              </option>`,
          )}
        </select></label
      ><label class="field"
        >Entry ID (manual alternative)<input
          .value=${this.config.entry_id ?? ""}
          @change=${(e: Event) =>
            this.change(
              "entry_id",
              (e.target as HTMLInputElement).value.trim(),
            )} /></label
      ><label class="field"
        >Initial series<select
          .value=${String(this.config.series_id ?? "")}
          @change=${(e: Event) =>
            this.change(
              "series_id",
              Number((e.target as HTMLSelectElement).value),
            )}
        >
          <option value="">First monitored series</option>
          ${[1, 2, 3].map(
            (s) => html`<option value=${s}>${SERIES[s]}</option>`,
          )}
        </select></label
      ><label class="field"
        >Initial view<select
          .value=${this.config.section ?? "Race Center"}
          @change=${(e: Event) =>
            this.change("section", (e.target as HTMLSelectElement).value)}
        >
          ${SECTIONS.map((s) => html`<option>${s}</option>`)}
        </select></label
      ><label class="field"
        >Title<input
          .value=${this.config.title ?? ""}
          placeholder="NASCAR Race Center"
          @change=${(e: Event) =>
            this.change("title", (e.target as HTMLInputElement).value.trim())}
      /></label>
    </div>`;
  }
}
defineOnce("nascar-race-center-card-editor", CardEditor);
