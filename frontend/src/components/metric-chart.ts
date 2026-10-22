import { defineOnce } from "../register";
import { LitElement, css, html, svg } from "lit";
import type { DataRow, Metric } from "../types";
import { label, number } from "../format";
import { styles } from "../styles";
interface Observation {
  driver: string;
  value: number | null;
  reason: string | null;
}
export interface MetricOption {
  key: string;
  name: string;
  classification: string;
  unit: string;
  method: string;
  observations: Observation[];
}
/** Group only identical source/metric/method/unit bases; never recompute a statistic. */
export function summaryOptions(rows: DataRow[]): MetricOption[] {
  const options = new Map<string, MetricOption>();
  const add = (driver: string, category: string, metric: Metric) => {
    const key = JSON.stringify([
      category,
      metric.name,
      metric.classification,
      metric.unit,
      metric.method,
    ]);
    const option = options.get(key) ?? {
      key,
      name: `${category} · ${label(metric.name)}`,
      classification: metric.classification,
      unit: metric.unit,
      method: metric.method,
      observations: [],
    };
    option.observations.push({
      driver,
      value: metric.value,
      reason: metric.reason,
    });
    options.set(key, option);
  };
  for (const row of rows) {
    if (!row.driver_id || !row.value) continue;
    if (row.kind === "driver")
      for (const metric of row.value.metrics)
        add(row.driver_id, "Lap summary", metric);
    if (row.kind === "performance" && row.value.result) {
      const r = row.value.result;
      for (const field of [
        "starting_position",
        "finishing_position",
        "laps_completed",
        "laps_led",
        "points_earned",
        "playoff_points_earned",
      ] as const) {
        add(row.driver_id, "Race result", {
          name: field,
          value: r[field],
          classification: "recorded",
          unit: field.includes("position")
            ? "position"
            : field.includes("laps")
              ? "lap_count"
              : "reported_points",
          method: "reported_result",
          reason: r[field] === null ? "not_reported" : null,
        });
      }
    }
    if (row.kind === "performance_stages") {
      const v = row.value;
      for (const field of ["position", "points"] as const)
        add(
          row.driver_id,
          `${label(v.dataset)} stage ${v.number}${v.run_id ? ` · ${v.run_namespace} ${v.run_id}` : ""}`,
          {
            name: field,
            value: v.conflict ? null : v[field],
            classification: "recorded",
            unit: field === "position" ? "position" : "reported_points",
            method: "reported_stage_observation",
            reason: v.conflict
              ? "conflicting_source_observations"
              : v[field] === null
                ? "not_reported"
                : null,
          },
        );
    }
    if (row.kind === "performance_reported_metrics") {
      const v = row.value;
      for (const m of v.metrics)
        add(
          row.driver_id,
          `${label(v.dataset)} · group ${v.source_index}${v.title ? ` · ${v.title}` : ""}`,
          {
            name: m.field,
            value: m.interpretation === "reported" ? m.value : null,
            classification: "recorded",
            unit: "source_unit_unverified",
            method: "reported_source_field",
            reason: m.interpretation === "reported" ? null : m.interpretation,
          },
        );
    }
  }
  return [...options.values()];
}
export class MetricChart extends LitElement {
  static properties = {
    rows: { attribute: false },
    selected: { state: true },
    locale: { type: String },
  };
  static styles = [
    styles,
    css`
      :host {
        display: block;
      }
      .comparison-scroll {
        overflow-x: auto;
      }
      .bars {
        min-width: 560px;
        width: 100%;
        display: block;
      }
      .axis {
        fill: var(--nrc-muted);
        font: 11px system-ui;
      }
      .bar {
        fill: color-mix(
          in srgb,
          var(--nrc-accent) 35%,
          var(--primary-text-color, #e8edf2)
        );
      }
      .baseline {
        stroke: var(--nrc-line);
      }
      table {
        white-space: normal;
      }
    `,
  ];
  rows: DataRow[] = [];
  selected = "";
  locale?: string;
  render() {
    const options = summaryOptions(this.rows);
    const selected = options.find((o) => o.key === this.selected) ?? options[0];
    if (!selected)
      return html`<div class="notice">
        Load pages containing driver summaries or supported
        race/stage/loop/average records to compare their metrics.
      </div>`;
    const values = selected.observations.flatMap((o) =>
      o.value === null ? [] : [o.value],
    );
    const min = Math.min(0, ...values),
      max = Math.max(0, ...values);
    const x = (value: number) => 165 + ((value - min) / (max - min || 1)) * 440;
    const unit = selected.unit.includes("unverified")
      ? "Source unit · unverified"
      : label(selected.unit);
    return html`<section class="panel stack">
      <h3>Compare loaded summary metrics</h3>
      <label class="field"
        >Metric and measurement basis<select
          .value=${selected.key}
          @change=${(e: Event) => {
            this.selected = (e.target as HTMLSelectElement).value;
          }}
        >
          ${options.map(
            (o) =>
              html`<option value=${o.key}>
                ${o.name} · ${label(o.classification)}
              </option>`,
          )}
        </select></label
      >
      <p class="muted">
        <small
          >${label(selected.classification)} · ${unit} ·
          ${label(selected.method)}. Loaded observations only.</small
        >
      </p>
      <div
        class="comparison-scroll"
        tabindex="0"
        role="region"
        aria-label="Summary comparison plot. Scroll for readable labels."
      >
        <svg
          class="bars"
          viewBox=${`0 0 700 ${selected.observations.length * 44 + 20}`}
          role="img"
          aria-label=${`${selected.name} comparison; exact values in the table below.`}
        >
          <line
            class="baseline"
            x1=${x(0)}
            x2=${x(0)}
            y1="0"
            y2=${selected.observations.length * 44}
          ></line>
          ${selected.observations.map(
            (o, i) =>
              svg`<text class="axis" x="8" y=${i * 44 + 24}>Driver ${o.driver}</text>${o.value !== null ? svg`<rect class="bar" x=${Math.min(x(0), x(o.value))} y=${i * 44 + 7} width=${Math.max(1, Math.abs(x(o.value) - x(0)))} height="25" rx="3"></rect>` : svg`<text class="axis" x="165" y=${i * 44 + 24}>Unavailable</text>`}<text class="axis" x="620" y=${i * 44 + 24}>${number(o.value, this.locale, 3)}</text>`,
          )}
        </svg>
      </div>
      <div
        class="table-scroll"
        tabindex="0"
        role="region"
        aria-label="Summary comparison values"
      >
        <table>
          <thead>
            <tr>
              <th>Driver</th>
              <th>Value · ${unit}</th>
              <th>Availability</th>
            </tr>
          </thead>
          <tbody>
            ${selected.observations.map(
              (o) =>
                html`<tr>
                  <td>${o.driver}</td>
                  <td>${number(o.value, this.locale, 6)}</td>
                  <td>
                    ${o.reason ? label(o.reason) : "Reported by analytics API"}
                  </td>
                </tr>`,
            )}
          </tbody>
        </table>
      </div>
    </section>`;
  }
}
defineOnce("nrc-metric-chart", MetricChart);
