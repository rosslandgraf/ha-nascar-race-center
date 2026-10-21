import { LitElement, css, html, nothing } from "lit";
import { repeat } from "lit/directives/repeat.js";
import type { Driver, Hass } from "../types";
import { number, numberLocale, sortedDrivers, type SortKey } from "../format";
import { styles } from "../styles";
export class Leaderboard extends LitElement {
  static properties = {
    rows: { attribute: false },
    hass: { attribute: false },
    sort: { state: true },
    descending: { state: true },
  };
  rows: Driver[] = [];
  hass?: Hass;
  sort: SortKey = "position";
  descending = false;
  static styles = [
    styles,
    css`
      :host {
        container-type: inline-size;
      }
      .tower {
        min-width: 960px;
      }
      th button {
        min-height: 32px;
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
        min-width: 190px;
      }
      .driver-button {
        border: 0;
        background: none;
        padding: 0;
        text-align: left;
        min-height: 36px;
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
          min-width: 700px;
        }
        .driver-cell {
          min-width: 160px;
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
          max-width: 145px;
        }
        .table-note {
          font-size: 11px;
        }
      }
    `,
  ];
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
      class=${extra}
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
    return html`<div
        class="table-scroll"
        tabindex="0"
        role="region"
        aria-label="Timing tower. Scroll horizontally for additional reported measurements."
      >
        <table class="tower">
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
              )}${this.heading(
                "Start",
                "starting_position",
                "desktop-extra",
              )}${this.heading("Change", "position_change")}${this.heading(
                "Gap*",
                "gap",
              )}${this.heading("Last*", "last_lap_time")}${this.heading(
                "Best*",
                "best_lap_time",
              )}${this.heading("Laps", "laps_completed")}
              <th scope="col">Speed*</th>
              <th scope="col">Status / pits</th>
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
                      @click=${() =>
                        this.dispatchEvent(
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
                        >Start ${number(d.starting_position, locale)} ·
                        ${d.running_status ?? "Status unknown"}</span
                      >
                    </button>
                  </td>
                  <td>
                    ${d.favorite
                      ? html`<span class="star" aria-label="Favorite">★</span>`
                      : "—"}
                  </td>
                  <td class="desktop-extra">
                    ${number(d.starting_position, locale)}
                  </td>
                  <td
                    class=${(d.position_change.value ?? 0) > 0
                      ? "positive"
                      : (d.position_change.value ?? 0) < 0
                        ? "negative"
                        : ""}
                  >
                    ${d.position_change.value != null &&
                    d.position_change.value > 0
                      ? "+"
                      : ""}${number(d.position_change.value, locale)}
                  </td>
                  <td>${number(d.gap, locale, 3)}</td>
                  <td>${number(d.last_lap_time, locale, 3)}</td>
                  <td>${number(d.best_lap_time, locale, 3)}</td>
                  <td>${number(d.laps_completed, locale)}</td>
                  <td>
                    <span title="Reported last / best / average speed"
                      >${number(d.last_lap_speed, locale, 3)} /
                      ${number(d.best_lap_speed, locale, 3)} /
                      ${number(d.average_speed, locale, 3)}</span
                    >
                  </td>
                  <td>
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
        starting position − current position (derived). On mobile, scroll for
        additional columns or open a driver.
      </p>`;
  }
}
customElements.define("nrc-leaderboard", Leaderboard);
