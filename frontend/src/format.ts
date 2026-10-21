import type { Driver, Hass, Live, Metric } from "./types";
export const label = (value: string | undefined | null) =>
  value ? value.replaceAll("_", " ") : "Unknown";
export function number(
  value: number | null | undefined,
  locale?: string,
  digits = 0,
): string {
  return typeof value === "number" && Number.isFinite(value)
    ? new Intl.NumberFormat(locale === "none" ? "en-US" : locale, {
        useGrouping: locale !== "none",
        maximumFractionDigits: digits,
      }).format(value)
    : "—";
}
export function instant(value: string | null | undefined): number | null {
  if (
    !value ||
    !/^\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d(?:\.\d+)?)?(?:Z|[+-]\d\d:\d\d)$/.test(
      value,
    )
  )
    return null;
  const time = Date.parse(value);
  return Number.isFinite(time) ? time : null;
}
export function date(value: string | null | undefined, hass?: Hass): string {
  const time = instant(value);
  if (time === null) return "Time unconfirmed";
  return new Intl.DateTimeFormat(hass?.locale?.language, {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: hass?.config?.time_zone,
    ...(hass?.locale?.time_format === "12"
      ? { hour12: true }
      : hass?.locale?.time_format === "24"
        ? { hour12: false }
        : {}),
  }).format(time);
}
export function countdown(
  value: string | null | undefined,
  now = Date.now(),
): string | null {
  const time = instant(value);
  if (time === null || time <= now) return null;
  const minutes = Math.ceil((time - now) / 60000);
  return minutes >= 1440
    ? `${Math.floor(minutes / 1440)}d ${Math.floor((minutes % 1440) / 60)}h`
    : `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}
export function freshness(live?: Live): { text: string; tone: string } {
  const code = live?.availability;
  return code === "ok" && live?.stale === false
    ? { text: "Fresh source", tone: "green" }
    : code === "stale" || live?.stale === true
      ? { text: "Stale · timing withheld", tone: "yellow" }
      : code === "freshness_unknown"
        ? { text: "Freshness unknown", tone: "yellow" }
        : { text: code ? label(code) : "Awaiting source", tone: "neutral" };
}
export function flag(live?: Live): { text: string; tone: string } {
  const known: Record<string, string> = {
    green: "green",
    yellow: "yellow",
    red: "red",
    white: "white",
    checkered: "checkered",
  };
  const name = live?.session?.flag;
  return name && known[name]
    ? { text: label(name), tone: known[name] }
    : {
        text:
          live?.session?.flag_state_code != null
            ? `Unknown flag (${live.session.flag_state_code})`
            : "Flag unreported",
        tone: "neutral",
      };
}
export type SortKey =
  | "position"
  | "name"
  | "car_number"
  | "starting_position"
  | "gap"
  | "last_lap_time"
  | "best_lap_time"
  | "laps_completed"
  | "position_change"
  | "favorite";
export function sortedDrivers(
  rows: Driver[],
  key: SortKey,
  descending = false,
): Driver[] {
  return rows
    .map((row, index) => ({ row, index }))
    .sort((a, b) => {
      const l =
        key === "position_change" ? a.row.position_change.value : a.row[key];
      const r =
        key === "position_change" ? b.row.position_change.value : b.row[key];
      if (l == null && r == null) return a.index - b.index;
      if (l == null) return 1;
      if (r == null) return -1;
      const cmp =
        typeof l === "number" && typeof r === "number"
          ? l - r
          : typeof l === "boolean" && typeof r === "boolean"
            ? Number(l) - Number(r)
            : String(l).localeCompare(String(r), undefined, { numeric: true });
      return (descending ? -cmp : cmp) || a.index - b.index;
    })
    .map((x) => x.row);
}
export function metricUnit(metric: Metric): string {
  return metric.unit.includes("unverified")
    ? "source unit · unverified"
    : label(metric.unit);
}

export function numberLocale(hass?: Hass): string | undefined {
  const selected = hass?.locale?.number_format;
  return selected === "none"
    ? "none"
    : selected === "comma_decimal"
      ? "en-US"
      : selected === "decimal_comma"
        ? "de-DE"
        : selected === "space_comma"
          ? "fr-FR"
          : selected === "system"
            ? undefined
            : hass?.locale?.language;
}
