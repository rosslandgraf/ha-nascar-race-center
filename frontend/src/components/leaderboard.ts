import { defineOnce } from "../register";
import { LitElement, css, html, nothing } from "lit";
import { repeat } from "lit/directives/repeat.js";
import type { Driver, Hass } from "../types";
import { number, numberLocale, sortedDrivers, type SortKey } from "../format";
import { messages } from "../messages";
import { styles } from "../styles";
export class Leaderboard extends LitElement {
  static properties = {
    rows: { attribute: false },
    hass: { attribute: false },
    sort: { state: true },
    descending: { state: true },
    expanded: { state: true },
    compact: { type: Boolean },
  };
  rows: Driver[] = [];
  hass?: Hass;
  sort: SortKey = "position";
  descending = false;
  expanded = false;
  compact = false;
  static styles = [
    styles,
    css`
      :host {
        container-type: inline-size;
      }
      .tower {
        min-width: 960px;
        table-layout: fixed;
      }
      th button {
        min-height: 44px;
        min-width: 44px;
        padding: 0;
        border: 0;
        background: none;
        font-size: inherit;
        text-transform: inherit;
        letter-spacing: inherit;
        color: inherit;
      }
      th button:hover {
        color: color-mix(
          in srgb,
          var(--nrc-accent) 35%,
          var(--primary-text-color, #e8edf2)
        );
      }
      td {
        font-size: 13px;
      }
      .driver-cell {
        width: 220px;
      }
      .driver-button {
        border: 0;
        background: none;
        padding: 0;
        text-align: left;
        min-height: 44px;
        width: 100%;
        overflow-wrap: anywhere;
        white-space: normal;
        font-weight: 650;
      }
      .favorite-row {
        background: color-mix(in srgb, var(--nrc-accent), transparent 96%);
      }
      .star {
        color: color-mix(
          in srgb,
          var(--nrc-accent) 35%,
          var(--primary-text-color, #e8edf2)
        );
        margin-right: 6px;
      }
      .rank {
        font-size: 19px;
        letter-spacing: -0.04em;
      }
      td.sticky,
      th.sticky {
        position: sticky;
        left: 0;
        background: var(--nrc-base);
        z-index: 1;
      }
      .table-scroll {
        max-height: 70vh;
      }
      th {
        position: sticky;
        top: 0;
        z-index: 2;
      }
      th.sticky {
        z-index: 3;
      }
      th:first-child,
      td:first-child {
        width: 54px;
      }
      th:nth-child(2),
      td:nth-child(2) {
        width: 64px;
      }
      th:nth-child(3) {
        width: 220px;
      }
      th:nth-child(11) {
        width: 185px;
      }
      th:last-child {
        width: 200px;
      }
      td {
        padding-block: 8px;
      }
      [data-compact] td {
        padding-block: 2px;
      }
      .column-toggle {
        display: none;
      }
      .tower-tools {
        display: flex;
        gap: 12px;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
        flex-wrap: wrap;
      }
      @container (max-width:600px) {
        .column-toggle {
          display: block;
        }
        th:first-child,
        td:first-child {
          width: 40px;
          padding-inline: 6px;
        }
        th:nth-child(2),
        td:nth-child(2) {
          width: 48px;
          padding-inline: 5px;
        }
        th:nth-child(3) {
          width: 150px;
        }
        th:nth-child(4) {
          width: 60px;
        }
        th:nth-child(11) {
          width: 185px;
        }
        th:last-child {
          width: 200px;
        }
        .tower:not([data-expanded]) .measurement {
          display: none;
        }
        .tower[data-expanded] {
          min-width: 1040px;
        }
        td:nth-child(2),
        th:nth-child(2) {
          position: sticky;
          left: 40px;
          background: var(--nrc-base);
          z-index: 1;
        }
        td:nth-child(3),
        th:nth-child(3) {
          position: sticky;
          left: 88px;
          background: var(--nrc-base);
          z-index: 1;
        }
        th:nth-child(2),
        th:nth-child(3) {
          z-index: 3;
        }
      }
      .mobile-metrics {
        display: none;
      }
      .positive {
        color: color-mix(
          in srgb,
          #a8ef75 35%,
          var(--primary-text-color, #e8edf2)
        );
      }
      .negative {
        color: color-mix(
          in srgb,
          #ff8d90 35%,
          var(--primary-text-color, #e8edf2)
        );
      }
      .table-note {
        font-size: 11px;
        color: var(--nrc-muted);
        padding: 10px 0;
      }
      @container (max-width:600px) {
        .tower {
          min-width: 340px;
        }
        .driver-cell {
          width: 150px;
        }
        .mobile-metrics {
          display: block;
          font-size: 11px;
          font-weight: 400;
          color: var(--nrc-muted);
        }
        td,
        th {
          padding: 10px;
        }
        .desktop-extra {
          display: none;
        }
        .rank {
          font-size: 17px;
        }
        .driver-button {
          white-space: normal;
          max-width: none;
        }
        .table-note {
          font-size: 11px;
        }
      }
    `,
  ];
  private moveFocus(event: KeyboardEvent) {
    if (!["ArrowDown", "ArrowUp", "Home", "End"].includes(event.key)) return;
    const buttons = [
      ...this.renderRoot.querySelectorAll<HTMLButtonElement>(".driver-button"),
    ];
    const index = buttons.indexOf(event.currentTarget as HTMLButtonElement);
    const next =
      event.key === "Home"
        ? 0
        : event.key === "End"
          ? buttons.length - 1
          : index + (event.key === "ArrowDown" ? 1 : -1);
    event.preventDefault();
    buttons[Math.max(0, Math.min(buttons.length - 1, next))]?.focus();
  }
  private order(key: SortKey) {
    if (key === this.sort) this.descending = !this.descending;
    else {
      this.sort = key;
      this.descending = false;
    }
  }
  private heading(text: string, key: SortKey, extra = "") {
    return html`<th
      scope="col"
      class=${extra + (key === "name" ? " driver-cell" : "")}
      aria-sort=${this.sort === key
        ? this.descending
          ? "descending"
          : "ascending"
        : "none"}
    >
      <button @click=${() => this.order(key)}>
        ${text}${this.sort === key ? (this.descending ? " ↓" : " ↑") : nothing}
      </button>
    </th>`;
  }
  render() {
    const locale = numberLocale(this.hass);
    return html`<div class="tower-tools">
        <small>${messages.sortHint}</small>
        <button
          class="column-toggle"
          aria-pressed=${this.expanded}
          @click=${() => {
            this.expanded = !this.expanded;
          }}
        >
          ${this.expanded ? messages.essential : messages.measurements}
        </button>
      </div>
      <p class="sr-only" role="status">
        Sorted by ${this.sort.replaceAll("_", " ")},
        ${this.descending ? "descending" : "ascending"}.
      </p>
      <div
        class="table-scroll"
        tabindex="0"
        role="region"
        aria-label="Timing tower. Scroll horizontally for additional reported measurements."
      >
        <table
          class="tower"
          ?data-expanded=${this.expanded}
          ?data-compact=${this.compact}
        >
          <caption class="sr-only">
            Full reported leaderboard. Activate a column to sort or a driver to
            open details. Timing and speed units are unverified.
          </caption>
          <thead>
            <tr>
              ${this.heading("Pos", "position", "sticky")}${this.heading(
                "Car",
                "car_number",
              )}${this.heading("Driver", "name")}${this.heading(
                "Fav",
                "favorite",
                "desktop-extra",
              )}${this.heading(
                "Start",
                "starting_position",
                "desktop-extra",
              )}${this.heading(
                "Change",
                "position_change",
                "desktop-extra",
              )}${this.heading("Gap*", "gap")}${this.heading(
                "Last*",
                "last_lap_time",
                "measurement",
              )}${this.heading(
                "Best*",
                "best_lap_time",
                "measurement",
              )}${this.heading("Laps", "laps_completed", "measurement")}
              <th scope="col" class="measurement">Speed*</th>
              <th scope="col" class="measurement">Status / pits</th>
            </tr>
          </thead>
          <tbody>
            ${repeat(
              sortedDrivers(this.rows, this.sort, this.descending),
              (d) => d.driver_id,
              (d) =>
                html`<tr class=${d.favorite ? "favorite-row" : ""}>
                  <td class="rank sticky">${number(d.position, locale)}</td>
                  <td><span class="car">${d.car_number ?? "—"}</span></td>
                  <td class="driver-cell">
                    <button
                      class="driver-button"
                      @keydown=${(e: KeyboardEvent) => this.moveFocus(e)}
                      @click=${(event: Event) =>
                        (event.currentTarget as HTMLElement).dispatchEvent(
                          new CustomEvent("driver-open", {
                            detail: d,
                            bubbles: true,
                            composed: true,
                          }),
                        )}
                    >
                      ${d.favorite
                        ? html`<span class="star" aria-label="Favorite"
                            >★</span
                          >`
                        : nothing}${d.name ?? `Driver ${d.driver_id}`}<span
                        class="mobile-metrics"
                        >Start ${number(d.starting_position, locale)} · Δ
                        ${d.position_change.value != null &&
                        d.position_change.value > 0
                          ? "+"
                          : ""}${number(d.position_change.value, locale)}
                        · ${d.running_status ?? "Status unknown"}</span
                      >
                    </button>
                  </td>
                  <td class="desktop-extra">
                    ${d.favorite
                      ? html`<span class="star" aria-label="Favorite">★</span>`
                      : "—"}
                  </td>
                  <td class="desktop-extra">
                    ${number(d.starting_position, locale)}
                  </td>
                  <td
                    class=${"desktop-extra " +
                    ((d.position_change.value ?? 0) > 0
                      ? "positive"
                      : (d.position_change.value ?? 0) < 0
                        ? "negative"
                        : "")}
                  >
                    ${d.position_change.value != null &&
                    d.position_change.value > 0
                      ? "+"
                      : ""}${number(d.position_change.value, locale)}
                  </td>
                  <td>${number(d.gap, locale, 3)}</td>
                  <td class="measurement">
                    ${number(d.last_lap_time, locale, 3)}
                  </td>
                  <td class="measurement">
                    ${number(d.best_lap_time, locale, 3)}
                  </td>
                  <td class="measurement">
                    ${number(d.laps_completed, locale)}
                  </td>
                  <td class="measurement">
                    <span title="Reported last / best / average speed"
                      >${number(d.last_lap_speed, locale, 3)} /
                      ${number(d.best_lap_speed, locale, 3)} /
                      ${number(d.average_speed, locale, 3)}</span
                    >
                  </td>
                  <td class="measurement">
                    ${d.running_status ?? "Unknown"} ·
                    ${d.pit_stops.total ?? "—"} pit observations
                  </td>
                </tr>`,
            )}
          </tbody>
        </table>
      </div>
      <p class="table-note">
        * Reported gap, lap-time and speed scales; units unverified. Change =
        starting position − current position (derived). ${messages.towerHint}
      </p>`;
  }
}
defineOnce("nrc-leaderboard", Leaderboard);
