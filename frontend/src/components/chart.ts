import { LitElement, css, html, svg, nothing } from "lit";
import type { DataRow } from "../types";
import { number } from "../format";
import { messages } from "../messages";
import { styles } from "../styles";
export type ChartMode = "time" | "position" | "delta" | "window";
export interface Point {
  lap: number;
  value: number | null;
}
export interface Series {
  id: string;
  points: Point[];
}
/** Only loaded observations are charted. Missing lap numbers/nulls always break paths. */
export function chartSeries(rows: DataRow[], mode: ChartMode): Series[] {
  const groups = new Map<string, Point[]>();
  for (const row of rows) {
    if (!row.driver_id) continue;
    let point: Point | undefined;
    if (row.kind === "samples" && row.value && mode !== "window") {
      const v = row.value;
      point = {
        lap: v.lap,
        value:
          mode === "position"
            ? v.usable_position
            : mode === "delta"
              ? v.consecutive_time_delta
              : v.valid_time && v.included_in_time_basis
                ? v.reported_time
                : null,
      };
    } else if (row.kind === "window" && row.value && mode === "window")
      point = { lap: row.value.last_lap, value: row.value.mean };
    if (point) {
      const points = groups.get(row.driver_id) ?? [];
      points.push(point);
      groups.set(row.driver_id, points);
    }
  }
  return [...groups].map(([id, points]) => ({
    id,
    points: points.sort((a, b) => a.lap - b.lap),
  }));
}
export function segments(points: Point[]): Point[][] {
  const result: Point[][] = [];
  let current: Point[] = [];
  for (const p of points) {
    if (p.value === null) {
      if (current.length) result.push(current);
      current = [];
      continue;
    }
    if (current.length && p.lap !== current.at(-1)!.lap + 1) {
      result.push(current);
      current = [];
    }
    current.push(p);
  }
  if (current.length) result.push(current);
  return result;
}
export class Chart extends LitElement {
  static properties = {
    rows: { attribute: false },
    mode: { type: String },
    locale: { type: String },
    inspected: { state: true },
  };
  rows: DataRow[] = [];
  mode: ChartMode = "time";
  locale?: string;
  inspected?: { id: string; lap: number };
  static styles = [
    styles,
    css`
      :host {
        display: block;
      }
      .chart-scroll {
        overflow-x: auto;
      }
      .graph {
        min-width: 560px;
        width: 100%;
        height: auto;
        display: block;
        min-height: 190px;
      }
      .grid {
        stroke: var(--nrc-line);
        stroke-width: 1;
      }
      .axis {
        fill: var(--nrc-muted);
        font-size: 11px;
        font-family: inherit;
      }
      .legend {
        display: flex;
        gap: 16px;
        flex-wrap: wrap;
        font-size: 12px;
      }
      .swatch {
        width: 12px;
        height: 3px;
        display: inline-block;
        vertical-align: middle;
        margin-right: 6px;
      }
      .inspector {
        display: flex;
        flex-wrap: wrap;
        align-items: end;
        gap: 12px;
        margin-top: 16px;
      }
      .inspection {
        min-height: 48px;
        padding-top: 12px;
        overflow-wrap: anywhere;
      }
      .legend button {
        min-height: 44px;
      }
      .legend [aria-pressed="true"] {
        border-color: currentColor;
        font-weight: 700;
      }
      circle {
        cursor: pointer;
      }
      .graph-wrap {
        border: 1px solid var(--nrc-line);
        border-radius: 10px;
        padding: 10px;
        background: var(--nrc-panel);
      }
      details {
        margin-top: 12px;
      }
      table {
        white-space: normal;
      }
    `,
  ];
  render() {
    const series = chartSeries(this.rows, this.mode);
    const valid = series
      .flatMap((s) => s.points)
      .filter((p): p is Point & { value: number } => p.value !== null);
    const titles = {
      time: "Lap-time progression",
      position: "Position progression",
      delta: "Consecutive-lap change",
      window: "Consecutive-window mean",
    };
    if (!series.length)
      return html`<div class="state">
        <h3>${titles[this.mode]}</h3>
        <p class="muted">
          No supported measurements on the loaded pages. Load the next page or
          change the selection.
        </p>
      </div>`;
    const selected =
      series.find((s) => s.id === this.inspected?.id) ?? series[0];
    const point =
      selected.points.find((p) => p.lap === this.inspected?.lap) ??
      selected.points[0];
    const pointIndex = selected.points.indexOf(point);
    const inspect = (id: string, lap: number) => {
      this.inspected = { id, lap };
    };
    const xs = series.flatMap((s) => s.points.map((p) => p.lap)),
      ys = valid.length ? valid.map((p) => p.value) : [0];
    const xmin = Math.min(...xs),
      xmax = Math.max(...xs),
      ymin = Math.min(...ys),
      ymax = Math.max(...ys);
    const padding = Math.max((ymax - ymin) * 0.12, 0.25);
    const lo = this.mode === "position" ? ymin : ymin - padding,
      hi = this.mode === "position" ? ymax : ymax + padding;
    const x = (v: number) =>
      xmin === xmax ? 380 : 55 + ((v - xmin) / (xmax - xmin)) * 650;
    const y = (v: number) =>
      this.mode === "position"
        ? hi === lo
          ? 135
          : 30 + ((v - lo) / (hi - lo)) * 210
        : 240 - ((v - lo) / (hi - lo || 1)) * 210;
    const colors = [
      "#a8ef75",
      "#84c5ff",
      "#f3c574",
      "#d8a2ed",
      "#fe9b97",
      "#80d6cf",
      "#ebc1ac",
      "#d8e1eb",
    ].map(
      (color) =>
        `color-mix(in srgb, ${color} 35%, var(--primary-text-color,#e8edf2))`,
    );
    return html`<div class="graph-wrap">
        <h3>${titles[this.mode]}</h3>
        <p class="muted">
          <small
            >${this.mode === "position"
              ? "Reported running positions"
              : this.mode === "time"
                ? "Reported measurements in selected basis · source unit unverified"
                : "Derived from selected observations · source unit unverified"}.
            ${messages.chartScope}</small
          >
        </p>
        ${!valid.length
          ? html`<p class="notice">
              No valid values on these pages. Missing observations remain
              inspectable below.
            </p>`
          : html`<div
              class="chart-scroll"
              tabindex="0"
              role="region"
              aria-label="Chart plot. Scroll horizontally for readable axes."
            >
              <svg
                class="graph"
                viewBox="0 0 740 280"
                role="img"
                aria-label=${titles[this.mode] +
                "; exact values available in the data table below."}
              >
                ${[0, 1, 2, 3, 4].map((i) => {
                  const v = lo + ((hi - lo) * i) / 4;
                  return svg`<line class="grid" x1="55" x2="705" y1=${y(v)} y2=${y(v)}></line><text class="axis" x="48" y=${y(v) + 4} text-anchor="end">${number(v, this.locale, 2)}</text>`;
                })}
                <text class="axis" x="55" y="267">
                  Lap ${number(xmin, this.locale)}
                </text>
                <text class="axis" x="705" y="267" text-anchor="end">
                  Lap ${number(xmax, this.locale)}
                </text>
                ${series.map((s, i) =>
                  segments(s.points).map(
                    (segment) =>
                      svg`<path d=${segment.map((p, j) => `${j ? "L" : "M"}${x(p.lap)},${y(p.value!)}`).join(" ")} fill="none" stroke=${colors[i % 8]} stroke-width="2.5" stroke-linejoin="round"></path>${segment.map((p) => svg`<circle cx=${x(p.lap)} cy=${y(p.value!)} r=${s.id === selected.id && p.lap === point.lap ? "5" : "3"} fill=${colors[i % 8]} @pointerenter=${() => inspect(s.id, p.lap)} @click=${() => inspect(s.id, p.lap)}><title>Driver ${s.id} · lap ${p.lap} · ${p.value}</title></circle>`)}`,
                  ),
                )}
                ${point.value !== null
                  ? svg`<line x1=${x(point.lap)} x2=${x(point.lap)} y1="25" y2="245" stroke="currentColor" stroke-dasharray="3 5" opacity="0.4"></line>`
                  : nothing}
              </svg>
            </div>`}
        <div class="legend" aria-label="Selected chart driver">
          ${series.map(
            (s, i) =>
              html`<button
                aria-pressed=${s.id === selected.id}
                @click=${() => inspect(s.id, s.points[0].lap)}
              >
                <i class="swatch" style=${`background:${colors[i % 8]}`}></i
                >Driver ${s.id}
              </button>`,
          )}
        </div>
        <div class="inspector" role="group" aria-label=${messages.inspect}>
          <label class="field"
            >Driver<select
              .value=${selected.id}
              @change=${(e: Event) => {
                const s = series.find(
                  (s) => s.id === (e.target as HTMLSelectElement).value,
                )!;
                inspect(s.id, s.points[0].lap);
              }}
            >
              ${series.map(
                (s) => html`<option value=${s.id}>Driver ${s.id}</option>`,
              )}
            </select></label
          >
          <label class="field"
            >Lap observation<select
              .value=${String(point.lap)}
              @change=${(e: Event) =>
                inspect(
                  selected.id,
                  Number((e.target as HTMLSelectElement).value),
                )}
            >
              ${selected.points.map(
                (p) =>
                  html`<option value=${p.lap}>
                    ${number(p.lap, this.locale)}${p.value === null
                      ? " · missing"
                      : ""}
                  </option>`,
              )}
            </select></label
          >
          <button
            aria-label=${messages.previousPoint}
            ?disabled=${pointIndex <= 0}
            @click=${() =>
              inspect(selected.id, selected.points[pointIndex - 1].lap)}
          >
            ←
          </button>
          <button
            aria-label=${messages.nextPoint}
            ?disabled=${pointIndex >= selected.points.length - 1}
            @click=${() =>
              inspect(selected.id, selected.points[pointIndex + 1].lap)}
          >
            →
          </button>
        </div>
        <p class="inspection" role="status">
          Driver ${selected.id} · lap ${number(point.lap, this.locale)} ·
          <strong
            >${point.value === null
              ? messages.missing
              : number(point.value, this.locale, 3)}</strong
          >
          ·
          ${this.mode === "position"
            ? "reported position"
            : this.mode === "time"
              ? "reported source measurement"
              : "derived source measurement"}
        </p>
        <p class="muted">
          <small
            >${series.reduce(
              (n, s) => n + s.points.filter((p) => p.value === null).length,
              0,
            )}
            explicit missing observations on loaded pages. Unloaded or absent
            laps are not interpolated.</small
          >
        </p>
      </div>
      <details>
        <summary>Exact chart data · accessible table</summary>
        <div
          class="table-scroll"
          tabindex="0"
          role="region"
          aria-label="Chart data"
        >
          <table>
            <thead>
              <tr>
                <th>Driver</th>
                <th>Lap</th>
                <th>Value (source unit / position)</th>
              </tr>
            </thead>
            <tbody>
              ${series.flatMap((s) =>
                s.points.map(
                  (p) =>
                    html`<tr>
                      <td>${s.id}</td>
                      <td>${number(p.lap, this.locale)}</td>
                      <td>
                        ${p.value === null
                          ? messages.missing
                          : number(p.value, this.locale, 3)}
                      </td>
                    </tr>`,
                ),
              )}
            </tbody>
          </table>
        </div>
      </details>`;
  }
}
customElements.define("nrc-chart", Chart);
