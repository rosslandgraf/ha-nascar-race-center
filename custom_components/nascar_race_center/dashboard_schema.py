"""Explicit dashboard v1 field allowlists over normalized immutable models.

No dataclass introspection, raw source dictionaries, HA Store or credentials.
Adding a model requires an intentional public-contract review here.
"""

from datetime import datetime
from enum import StrEnum
from math import isfinite
from typing import Any

from . import analytics_models as a
from . import history_models as h
from . import models as m
from . import reference as r
from . import scoring as s
from . import timing as t

FIELDS: dict[type, str] = {
    m.Session: "session_id name kind start_time end_time status notes run_type_code",
    m.Race: (
        "series_id season race_id name start_time track track_id status"
        " sessions_failed sessions"
    ),
    r.DriverAssociation: "series_id series_label car_number team manufacturer team_raw",
    r.Track: "track_id name city state length_miles track_type surface",
    t.LedInterval: "start_lap end_lap",
    s.PitStop: (
        "lap leader_lap entry_time exit_time entry_position "
        "exit_position position_change"
    ),
    s.CurrentStage: "number finish_at_lap laps_in_stage",
    s.RaceContext: "series_id season race_id run_id run_namespace",
    s.Provenance: "endpoint scope source_updated_at",
    s.PitActivity: (
        "car_number driver_name stop stop_type total_duration "
        "stop_duration box_stop_time box_leave_time in_travel_duration "
        "out_travel_duration entry_flag_code exit_flag_code "
        "tires_changed"
    ),
    s.StageResult: "driver_id position points car_number",
    s.StageClassification: "context number results",
    s.DriverPoints: (
        "context driver_id membership_id position points race_points "
        "bonus_points stage_points stage_winner delta_leader delta_next"
        " eligible wins top_five top_ten poles fastest_lap_point"
    ),
    h.HistoricalRaceKey: "season series_id race_id",
    h.HistoricalDriver: "nascar_driver_id car_number name manufacturer",
    h.HistoricalResult: (
        "driver result_id results_run_id finishing_position "
        "starting_position laps_completed laps_led points_earned "
        "playoff_points_earned finishing_status disqualified "
        "official_car_number vehicle_number team_id team_name "
        "best_lap_time best_lap_speed owner_id crew_chief_id"
    ),
    h.HistoricalLeader: "start_lap end_lap car_number",
    h.HistoricalCaution: (
        "start_lap end_lap flag_code reason comment beneficiary_car_number"
    ),
    h.WeekendScheduleItem: "name run_type_code start_time_utc_reported notes",
    h.HistoricalLap: "lap lap_time lap_speed running_position",
    h.HistoricalFlag: "laps_completed flag_code",
    h.HistoricalNote: "lap note_id flag_code text reported_driver_ids",
    h.ReportedMetric: "field value interpretation",
    h.HistoricalLoopDriver: "nascar_driver_id metrics",
    h.HistoricalAverageDriver: "driver sponsor metrics",
    h.HistoricalPit: "activity manufacturer reported_numbers nascar_driver_id",
    h.HistoryProvenance: (
        "dataset requested validation coverage delivery retrieved_at "
        "response_at http_status retry_after"
    ),
    a.AnalyticsQuery: "key driver_ids first_lap last_lap windows time_basis",
    a.Metric: "name value method unit classification reason",
    a.DatasetEvidence: "dataset status provenance reason",
    a.LapGap: "first_lap last_lap",
    a.LapSample: (
        "lap source_index reported_time reported_position valid_time "
        "time_exclusion usable_position included_in_time_basis "
        "consecutive_time_delta"
    ),
    a.Coverage: (
        "requested_laps recorded_laps missing_laps missing_times "
        "invalid_times valid_times basis_samples basis_excluded "
        "usable_positions out_of_range"
    ),
    a.ConsecutiveRun: "first_lap last_lap sample_count",
    a.RollingWindow: "first_lap last_lap sample_count mean median minimum maximum",
    a.PositionPoint: "lap position source_index",
    a.RelativeMetric: "name left_value right_value difference relative_percent",
    a.DriverComparison: (
        "left_driver_id right_driver_id left_sample_count right_sample_count metrics"
    ),
    a.ReportedMetricGroup: "dataset source_index title metrics classification",
    a.StageObservation: "dataset number run_namespace run_id position points conflict",
    a.SessionPerformance: "weekend_run_id timing_run_id label result",
}


def fields(value: object, names: str) -> dict[str, Any]:
    """Copy only named contract fields; identifiers are lossless decimal strings."""
    result: dict[str, Any] = {}
    for name in names.split():
        item = getattr(value, name)
        if name.endswith("_ids") and name != "series_ids":
            result[name] = [str(i) for i in item]
        elif name.endswith("_id") and name != "series_id":
            result[name] = str(item) if item is not None else None
        else:
            result[name] = project(item)
    return result


def project(value: object) -> Any:
    """Serialize only registered normalized types and finite JSON primitives."""
    if value is None or isinstance(value, str | bool | int | StrEnum):
        return value
    if isinstance(value, float):
        return value if isfinite(value) else None
    if isinstance(value, datetime):
        return value.isoformat() if value.utcoffset() is not None else None
    if isinstance(value, tuple):
        return [project(item) for item in value]
    if type(value) not in FIELDS:
        raise ValueError("Unregistered dashboard model")
    return fields(value, FIELDS[type(value)])
