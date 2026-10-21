import { html, nothing, type TemplateResult } from "lit";
import type { DataRow, Hass, Metric, Page } from "../types";
import { date, label, metricUnit, number } from "../format";
export function values(value: unknown, depth = 0): TemplateResult | string {
  if (value == null) return "Unknown / not reported";
  if (typeof value === "boolean") return value ? "Yes" : "No";
  if (typeof value === "number") return number(value, undefined, 6);
  if (typeof value === "string") return value;
  if (depth > 6) return "Nested observation";
  if (Array.isArray(value))
    return value.length
      ? html`${value.map(
          (v, i) =>
            html`<div>
              ${value.length > 1
                ? html`<small>Observation ${i + 1}</small>`
                : nothing}${values(v, depth + 1)}
            </div>`,
        )}`
      : "No reported records";
  return html`<dl>
    ${Object.entries(value).map(
      ([k, v]) =>
        html`<dt>${label(k)}</dt>
          <dd>${values(v, depth + 1)}</dd>`,
    )}
  </dl>`;
}
export function records(rows: DataRow[]) {
  return html`<div class="record-list">
    ${rows.map(
      (row, i) =>
        html`<details>
          <summary>
            ${label(row.kind)}${row.driver_id
              ? ` · driver ${row.driver_id}`
              : ""}${row.number != null
              ? ` · stage ${row.number}`
              : ""}${row.size ? ` · ${row.size} laps` : ""}${row.source_index !=
            null
              ? ` · source index ${row.source_index}`
              : ` · record ${i + 1}`}
          </summary>
          ${values(row.value ?? row.best_mean ?? row)}
        </details>`,
    )}
  </div>`;
}
export function evidence(page: Page, hass?: Hass) {
  const entries = page.evidence ?? page.datasets ?? [];
  return html`<div class="evidence">
    ${entries.map(
      (e) =>
        html`<details>
          <summary class="badge">
            ${"dataset" in e ? e.dataset : (e.provenance?.dataset ?? "Dataset")}
            · ${label(e.status)}
          </summary>
          <dl>
            <dt>Reason</dt>
            <dd>${label(e.reason)}</dd>
            <dt>Identity validation</dt>
            <dd>${label(e.provenance?.validation)}</dd>
            <dt>Coverage</dt>
            <dd>${label(e.provenance?.coverage)}</dd>
            <dt>Retrieved</dt>
            <dd>${date(e.provenance?.retrieved_at, hass)}</dd>
            <dt>Reported content time</dt>
            <dd>${date(e.provenance?.response_at, hass)}</dd>
            <dt>Delivery</dt>
            <dd>${label(e.provenance?.delivery)}</dd>
            <dt>Retry after</dt>
            <dd>${e.provenance?.retry_after ?? "Unknown"}</dd>
          </dl>
        </details>`,
    )}
  </div>`;
}
export function metricCard(m: Metric, locale?: string) {
  return html`<div class="panel metric">
    <h3>${label(m.name)}</h3>
    <strong>${number(m.value, locale, 3)}</strong>
    <p>${label(m.classification)} · ${metricUnit(m)}</p>
    <details>
      <summary>Method & availability</summary>
      <p>${label(m.method)}${m.reason ? ` · ${label(m.reason)}` : ""}</p>
    </details>
  </div>`;
}
export function resultTable(rows: DataRow[], hass?: Hass) {
  const results = rows.filter((r) => r.kind === "result");
  return results.length
    ? html`<div
        class="table-scroll"
        role="region"
        aria-label="Historical reported results"
        tabindex="0"
      >
        <table>
          <caption class="sr-only">
            Reported historical results; no assertion of official finality.
          </caption>
          <thead>
            <tr>
              <th>Finish</th>
              <th>Driver</th>
              <th>Start</th>
              <th>Laps</th>
              <th>Led</th>
              <th>Points</th>
              <th>Playoff</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${results.map((r) => {
              const v = r.value!;
              return html`<tr>
                <td>${number(v.finishing_position, hass?.locale?.language)}</td>
                <td>
                  <span class="car">${v.driver.car_number ?? "—"}</span> ${v
                    .driver.name ?? v.driver.nascar_driver_id}
                </td>
                <td>${number(v.starting_position)}</td>
                <td>${number(v.laps_completed)}</td>
                <td>${number(v.laps_led)}</td>
                <td>${number(v.points_earned)}</td>
                <td>${number(v.playoff_points_earned)}</td>
                <td>${v.finishing_status ?? "Unknown"}</td>
              </tr>`;
            })}
          </tbody>
        </table>
      </div>`
    : nothing;
}
