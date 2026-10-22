/** Leaf models are imported from the reviewed Phase 5A contract. */
import type * as API from "../../docs/DASHBOARD_API_MODELS";
export type {
  Race,
  Session,
  Metric,
  LapSample,
} from "../../docs/DASHBOARD_API_MODELS";
export type Section =
  | "Race Center"
  | "Live Timing"
  | "Race Weekend"
  | "History"
  | "Analytics";
export const SECTIONS: Section[] = [
  "Race Center",
  "Live Timing",
  "Race Weekend",
  "History",
  "Analytics",
];
export const SERIES: Record<number, string> = {
  1: "Cup Series",
  2: "National Series 2",
  3: "Truck Series",
};
export const DATASETS = [
  "weekend",
  "laps",
  "notes",
  "loop",
  "averages",
  "pits",
  "stages",
] as const;
export type Dataset = (typeof DATASETS)[number];
export type Unsubscribe = () => void | Promise<void>;
export interface Connection {
  subscribeMessage<T>(
    callback: (message: T) => void,
    request: Record<string, unknown>,
  ): Promise<Unsubscribe>;
  addEventListener(type: "ready" | "disconnected", callback: () => void): void;
  removeEventListener(
    type: "ready" | "disconnected",
    callback: () => void,
  ): void;
}
export interface Hass {
  callWS<T>(request: Record<string, unknown>): Promise<T>;
  connection: Connection;
  user?: { is_admin: boolean };
  locale?: {
    language?: string;
    time_format?: "12" | "24" | "language" | "system";
    number_format?: string;
  };
  config?: { time_zone?: string };
}
export interface CardConfig {
  type: string;
  entry_id?: string;
  series_id?: number;
  section?: Section;
  title?: string;
}
export interface Entry {
  entry_id: string;
  domain: string;
  title: string;
  state: string;
}
export interface Envelope<T> {
  api_version: 1;
  entry_id: string;
  data: T;
  revision?: number;
}
export interface RaceSummary extends Omit<API.Race, "sessions"> {
  session_count?: number;
  sessions?: API.Session[];
  sessions_complete?: boolean;
}
export interface Bootstrap {
  series_ids: number[];
  favorite_driver_ids: string[];
  provider: string;
  references: {
    drivers_status: string;
    tracks_status: string;
    unresolved_favorites: { driver_id: string; reason: string }[];
    drivers: {
      driver_id: string;
      name: string;
      associations: {
        series_id: number;
        metadata: API.DriverAssociation | null;
        reason: string | null;
      }[];
    }[];
    tracks: API.Track[];
  };
  navigation: {
    series_id: number;
    seasons: number[];
    race_count: number;
    unknown_start_count: number;
    failed_seasons: number[];
  }[];
  upcoming: RaceSummary[];
  upcoming_complete: boolean;
  next_activity: {
    start_time: string;
    race: RaceSummary;
    session: API.Session | null;
  } | null;
  next_activity_reason: string | null;
  source_state: { series_id: number; live: string; schedule: string }[];
  supported_sessions: string[];
  capabilities: {
    history_datasets: Dataset[];
    analytics_contract_version: number;
    access: string;
    live_push: boolean;
  };
  limitations: string[];
}
export interface Preview<T> {
  records: T[] | null;
  total: number | null;
  complete: boolean;
  detail_command: string;
}
export interface Driver extends API.LiveReportedDriver {
  favorite: boolean;
  running_status: string | null;
  position_change: {
    value: number | null;
    classification: "derived";
    method: string;
  };
  pit_stops: Preview<API.PitStop>;
  laps_led: Preview<API.LedInterval>;
}
export interface Live {
  session_state?: string | null;
  observation_advancement?: string;
  identity: {
    series_id: number;
    season: number | null;
    race_id: string | null;
    run_id: string | null;
    season_basis: string;
  };
  availability: string;
  source_updated_at: string | null;
  stale: boolean | null;
  session: {
    run_name: string | null;
    status: string | null;
    run_type_code: number | null;
    flag: string | null;
    flag_state_code: number | null;
    lap: number | null;
    total_laps: number | null;
    laps_remaining: number | null;
    elapsed_seconds: number | null;
    leaderboard_failed: boolean;
    stage_failed: boolean;
    progress: string;
    stage: API.CurrentStage | null;
  } | null;
  leader_driver_id: string | null;
  leaderboard: Driver[] | null;
  reported_count: number | null;
  omitted_count: number | null;
  scoring: Record<
    "pits" | "stages" | "points",
    Preview<API.PitActivity | API.StageClassification | API.DriverPoints> & {
      status: string;
      provenance: API.Provenance | null;
      classification: string;
    }
  >;
  limitations: string[];
}
export interface Pagination {
  offset: number;
  limit: number;
  returned: number;
  total: number;
  next_offset: number | null;
  snapshot: string;
  complete: boolean;
}
export interface RowValues {
  race: RaceSummary;
  session: API.Session | API.HistoricalSessionHeader;
  weekend: API.HistoricalWeekendHeader;
  result: API.HistoricalResult;
  session_result: API.HistoricalResult;
  leaders: API.HistoricalLeader;
  cautions: API.HistoricalCaution;
  schedule: API.WeekendScheduleItem;
  weekend_stage: never;
  stage: never;
  weekend_stage_result: API.StageResult;
  stage_result: API.StageResult;
  lap_driver: API.DriverLapsHeader;
  lap: API.HistoricalLap;
  flags: API.HistoricalFlag;
  notes: API.HistoricalNote;
  pits: API.HistoricalPit;
  loop: API.HistoricalLoopHeader;
  average: never;
  loop_driver: API.HistoricalLoopDriver;
  average_driver: API.HistoricalAverageDriver;
  driver: API.AnalyticsDriverSummary;
  samples: API.LapSample;
  gaps: API.LapGap;
  consecutive_runs: API.ConsecutiveRun;
  window_summary: never;
  window: API.RollingWindow;
  position_summary: API.AnalyticsPositionSummary;
  position_points: API.PositionPoint;
  position_gaps: API.LapGap;
  comparison: API.DriverComparison;
  performance: API.AnalyticsPerformanceSummary;
  performance_stages: API.StageObservation;
  performance_reported_metrics: API.ReportedMetricGroup;
  performance_sessions: API.SessionPerformance;
  pit_stop: API.PitStop;
  laps_led: API.LedInterval;
  detail: unknown;
}
export type DataRow = {
  [K in keyof RowValues]: {
    kind: K;
    value?: RowValues[K];
    dataset?: Dataset;
    driver_id?: string;
    source_index?: number;
    size?: number;
    number?: number;
    title?: string | null;
    best_mean?: API.Metric;
    race_id?: string;
    season?: number | null;
    weekend_run_id?: string;
    context?: API.RaceContext;
  };
}[keyof RowValues];
export interface Page {
  records: DataRow[];
  pagination: Pagination;
  status?: string;
  availability?: string;
  reason?: string | null;
  race?: API.HistoricalRaceKey;
  datasets?: {
    status: string;
    reason: string | null;
    classification: string;
    provenance: API.HistoryProvenance;
  }[];
  evidence?: API.DatasetEvidence[];
  contract_version?: number;
  query?: API.AnalyticsQuery;
  race_metrics?: API.Metric[];
  caveats?: string[];
  identity?: {
    series_id: number | null;
    race_id: string | null;
    run_id: string | null;
    source_updated_at?: string | null;
  } | null;
  provenance?: API.Provenance | null;
  collection?: string;
  driver_id?: string;
}
export type PageCommand =
  | "schedule"
  | "history"
  | "analytics"
  | "live_driver"
  | "live_scoring";
export type PageSelection = {
  series_id: number;
  season?: number;
  race_id?: number;
  datasets?: Dataset[];
  driver_ids?: number[];
  first_lap?: number;
  last_lap?: number;
  windows?: number[];
  time_basis?: "all_available" | "overlapping_valid_laps";
  driver_id?: number;
  collection?: string;
};
