// Dashboard API v1 normalized model declarations; documentation only.
// No frontend assets or runtime package. Dates are ISO strings; source date labels remain unparsed.
// IDs use lossless decimal strings. Requests use bounded integer IDs (see DASHBOARD_API.md).

export interface Session {
  session_id: string;
  name: string;
  kind: string | null;
  start_time: string | null;
  end_time: string | null;
  status: string | null;
  notes: string | null;
  run_type_code: number | null;
}

export interface Race {
  series_id: number;
  season: number | null;
  race_id: string;
  name: string;
  start_time: string | null;
  track: string | null;
  track_id: string | null;
  status: string | null;
  sessions_failed: boolean;
  sessions: Array<Session>;
}

export interface DriverAssociation {
  series_id: number | null;
  series_label: string | null;
  car_number: string | null;
  team: string | null;
  manufacturer: string | null;
  team_raw: string | null;
}

export interface Track {
  track_id: string;
  name: string;
  city: string | null;
  state: string | null;
  length_miles: number | null;
  track_type: string | null;
  surface: string | null;
}

export interface LedInterval {
  start_lap: number;
  end_lap: number;
}

export interface PitStop {
  lap: number | null;
  leader_lap: number | null;
  entry_time: number | null;
  exit_time: number | null;
  entry_position: number | null;
  exit_position: number | null;
  position_change: number | null;
}

export interface CurrentStage {
  number: number | null;
  finish_at_lap: number | null;
  laps_in_stage: number | null;
}

export interface RaceContext {
  series_id: number | null;
  season: number | null;
  race_id: string | null;
  run_id: string | null;
  run_namespace: string | null;
}

export interface Provenance {
  endpoint: string;
  scope: "global" | "embedded" | "historical" | "synthetic";
  source_updated_at: string | null;
}

export interface PitActivity {
  car_number: string | null;
  driver_name: string | null;
  stop: PitStop;
  stop_type: string | null;
  total_duration: number | null;
  stop_duration: number | null;
  box_stop_time: number | null;
  box_leave_time: number | null;
  in_travel_duration: number | null;
  out_travel_duration: number | null;
  entry_flag_code: number | null;
  exit_flag_code: number | null;
  tires_changed: Array<boolean | null>;
}

export interface StageResult {
  driver_id: string;
  position: number | null;
  points: number | null;
  car_number: string | null;
}

export interface StageClassification {
  context: RaceContext;
  number: number;
  results: Array<StageResult>;
}

export interface DriverPoints {
  context: RaceContext;
  driver_id: string;
  membership_id: string | null;
  position: number | null;
  points: number | null;
  race_points: number | null;
  bonus_points: number | null;
  stage_points: Array<number | null>;
  stage_winner: Array<boolean | null>;
  delta_leader: number | null;
  delta_next: number | null;
  eligible: boolean | null;
  wins: number | null;
  top_five: number | null;
  top_ten: number | null;
  poles: number | null;
  fastest_lap_point: boolean | null;
}

export interface HistoricalRaceKey {
  season: number;
  series_id: number;
  race_id: string;
}

export interface HistoricalDriver {
  nascar_driver_id: string;
  car_number: string | null;
  name: string | null;
  manufacturer: string | null;
}

export interface HistoricalResult {
  driver: HistoricalDriver;
  result_id: string | null;
  results_run_id: string | null;
  finishing_position: number | null;
  starting_position: number | null;
  laps_completed: number | null;
  laps_led: number | null;
  points_earned: number | null;
  playoff_points_earned: number | null;
  finishing_status: string | null;
  disqualified: boolean | null;
  official_car_number: string | null;
  vehicle_number: string | null;
  team_id: string | null;
  team_name: string | null;
  best_lap_time: number | null;
  best_lap_speed: number | null;
  owner_id: string | null;
  crew_chief_id: string | null;
}

export interface HistoricalLeader {
  start_lap: number | null;
  end_lap: number | null;
  car_number: string | null;
}

export interface HistoricalCaution {
  start_lap: number | null;
  end_lap: number | null;
  flag_code: number | null;
  reason: string | null;
  comment: string | null;
  beneficiary_car_number: string | null;
}

export interface WeekendScheduleItem {
  name: string | null;
  run_type_code: number | null;
  start_time_utc_reported: string | null;
  notes: string | null;
}

export interface HistoricalLap {
  lap: number;
  lap_time: number | null;
  lap_speed: number | null;
  running_position: number | null;
}

export interface HistoricalFlag {
  laps_completed: number;
  flag_code: number | null;
}

export interface HistoricalNote {
  lap: number;
  note_id: string | null;
  flag_code: number | null;
  text: string | null;
  reported_driver_ids: Array<string>;
}

export interface ReportedMetric {
  field: string;
  value: number | number | null;
  interpretation: "reported" | "candidate_sentinel" | "missing";
}

export interface HistoricalLoopDriver {
  nascar_driver_id: string;
  metrics: Array<ReportedMetric>;
}

export interface HistoricalAverageDriver {
  driver: HistoricalDriver;
  sponsor: string | null;
  metrics: Array<ReportedMetric>;
}

export interface HistoricalPit {
  activity: PitActivity;
  manufacturer: string | null;
  reported_numbers: Array<ReportedMetric>;
  nascar_driver_id: string | null;
}

export interface HistoryProvenance {
  dataset: "weekend" | "laps" | "notes" | "loop" | "averages" | "pits" | "stages";
  requested: HistoricalRaceKey;
  validation: "reported_identity" | "path_context_only" | "not_validated" | "fictional";
  coverage: "observed_example" | "unverified_context" | "fictional";
  delivery: string;
  retrieved_at: string;
  response_at: string | null;
  http_status: number | null;
  retry_after: number | null;
}

export interface AnalyticsQuery {
  key: HistoricalRaceKey;
  driver_ids: Array<string>;
  first_lap: number;
  last_lap: number;
  windows: Array<number>;
  time_basis: "all_available" | "overlapping_valid_laps";
}

export interface Metric {
  name: string;
  value: number | number | null;
  method: string;
  unit: string;
  classification: "derived" | "recorded";
  reason: string | null;
}

export interface DatasetEvidence {
  dataset: "weekend" | "laps" | "notes" | "loop" | "averages" | "pits" | "stages";
  status: "available" | "empty" | "not_yet_published" | "unsupported_unverified" | "partial" | "network_access_failure" | "invalid_schema_identity";
  provenance: HistoryProvenance | null;
  reason: string | null;
}

export interface LapGap {
  first_lap: number;
  last_lap: number;
}

export interface LapSample {
  lap: number;
  source_index: number;
  reported_time: number | null;
  reported_position: number | null;
  valid_time: boolean;
  time_exclusion: string | null;
  usable_position: number | null;
  included_in_time_basis: boolean;
  consecutive_time_delta: number | null;
}

export interface Coverage {
  requested_laps: number;
  recorded_laps: number;
  missing_laps: number;
  missing_times: number;
  invalid_times: number;
  valid_times: number;
  basis_samples: number;
  basis_excluded: number;
  usable_positions: number;
  out_of_range: number;
}

export interface ConsecutiveRun {
  first_lap: number;
  last_lap: number;
  sample_count: number;
}

export interface RollingWindow {
  first_lap: number;
  last_lap: number;
  sample_count: number;
  mean: number;
  median: number;
  minimum: number;
  maximum: number;
}

export interface PositionPoint {
  lap: number;
  position: number;
  source_index: number;
}

export interface RelativeMetric {
  name: string;
  left_value: number | number | null;
  right_value: number | number | null;
  difference: Metric;
  relative_percent: Metric;
}

export interface DriverComparison {
  left_driver_id: string;
  right_driver_id: string;
  left_sample_count: number;
  right_sample_count: number;
  metrics: Array<RelativeMetric>;
}

export interface ReportedMetricGroup {
  dataset: "weekend" | "laps" | "notes" | "loop" | "averages" | "pits" | "stages";
  source_index: number;
  title: string | null;
  metrics: Array<ReportedMetric>;
  classification: "recorded";
}

export interface StageObservation {
  dataset: "weekend" | "laps" | "notes" | "loop" | "averages" | "pits" | "stages";
  number: number;
  run_namespace: "stage_run" | null;
  run_id: string | null;
  position: number | null;
  points: number | null;
  conflict: boolean;
}

export interface SessionPerformance {
  weekend_run_id: string;
  timing_run_id: string | null;
  label: string | null;
  result: HistoricalResult | null;
}

export interface HistoricalWeekendHeader {
  key: HistoricalRaceKey;
  name: string | null;
  track_id: string | null;
  track_name: string | null;
  timing_run_id: string | null;
  scheduled_laps: number | null;
  actual_laps: number | null;
  scheduled_distance: number | null;
  actual_distance: number | null;
  date_scheduled_reported: string | null;
  race_date_reported: string | null;
  inspection_complete: boolean | null;
  master_race_id: string | null;
  race_type_code: number | null;
}

export interface HistoricalSessionHeader {
  weekend_run_id: string;
  timing_run_id: string | null;
  run_type_code: number | null;
  name: string | null;
  run_date: string | null;
  run_date_utc: string | null;
}

export interface DriverLapsHeader {
  driver: HistoricalDriver;
  running_position: number | null;
}

export interface HistoricalLoopHeader {
  name: string | null;
  scheduled_laps: number | null;
  actual_laps: number | null;
}

export interface AnalyticsDriverSummary {
  status: "available" | "partial" | "unavailable" | "invalid";
  reason: string | null;
  coverage: Coverage;
  metrics: Array<Metric>;
  fastest_lap: number | null;
}

export interface AnalyticsPositionSummary {
  start: PositionPoint | null;
  end: PositionPoint | null;
  change: Metric;
  best: Metric;
  worst: Metric;
  first_position_samples: Metric;
}

export interface AnalyticsPerformanceSummary {
  result: HistoricalResult | null;
  result_reason: string | null;
  start_finish_position_change: Metric;
  reported_position_difference: Metric;
}

export interface LiveReportedDriver {
  driver_id: string;
  name: string | null;
  car_number: string | null;
  manufacturer: string | null;
  position: number | null;
  starting_position: number | null;
  laps_completed: number | null;
  last_lap_time: number | null;
  best_lap_time: number | null;
  last_lap_speed: number | null;
  best_lap_speed: number | null;
  average_speed: number | null;
  gap: number | null;
  status_code: number | null;
  is_on_track: boolean | null;
  pits_failed: boolean;
}
