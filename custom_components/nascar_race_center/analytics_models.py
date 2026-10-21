"""Immutable internal analytics contract v1; no HA, transport or provider JSON."""

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Literal

from .history_models import (
    HistoricalRaceKey,
    HistoricalResult,
    HistoryDataset,
    HistoryProvenance,
    HistoryStatus,
    ReportedMetric,
)

MAX_SELECTED_DRIVERS = 8
MAX_LAP_SPAN = 5000
MAX_ROLLING_POINTS = 60000
WINDOW_CHOICES = (5, 10, 15, 20, 25, 30)


class AnalyticsStatus(StrEnum):
    AVAILABLE = "available"
    PARTIAL = "partial"
    UNAVAILABLE = "unavailable"
    INVALID = "invalid"


@dataclass(frozen=True, slots=True)
class AnalyticsQuery:
    key: HistoricalRaceKey
    driver_ids: tuple[int, ...]
    first_lap: int = 0
    last_lap: int = 4999
    windows: tuple[int, ...] = (5,)
    time_basis: Literal["all_available", "overlapping_valid_laps"] = "all_available"

    def __post_init__(self) -> None:
        if (
            not isinstance(self.key, HistoricalRaceKey)
            or not isinstance(self.driver_ids, tuple)
            or not 1 <= len(self.driver_ids) <= MAX_SELECTED_DRIVERS
            or any(type(d) is not int or not 1 <= d <= 10**10 for d in self.driver_ids)
            or len(set(self.driver_ids)) != len(self.driver_ids)
            or type(self.first_lap) is not int
            or type(self.last_lap) is not int
            or not 0 <= self.first_lap <= self.last_lap <= 10**10
            or self.last_lap - self.first_lap >= MAX_LAP_SPAN
            or not isinstance(self.windows, tuple)
            or len(self.windows) > len(WINDOW_CHOICES)
            or any(type(n) is not int or n not in WINDOW_CHOICES for n in self.windows)
            or len(set(self.windows)) != len(self.windows)
            or self.time_basis not in ("all_available", "overlapping_valid_laps")
            or (
                len(self.driver_ids)
                * (self.last_lap - self.first_lap + 1)
                * len(self.windows)
                > MAX_ROLLING_POINTS
            )
        ):
            raise ValueError("Invalid or excessive analytics selection")


@dataclass(frozen=True, slots=True)
class Metric:
    name: str
    value: float | int | None
    method: str
    unit: str
    classification: Literal["derived", "recorded"] = "derived"
    reason: str | None = None

    @property
    def available(self) -> bool:
        return self.value is not None


@dataclass(frozen=True, slots=True)
class DatasetEvidence:
    dataset: HistoryDataset
    status: HistoryStatus
    provenance: HistoryProvenance | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class LapGap:
    first_lap: int
    last_lap: int


@dataclass(frozen=True, slots=True)
class LapSample:
    lap: int
    source_index: int
    reported_time: float | None
    reported_position: int | None
    valid_time: bool
    time_exclusion: str | None
    usable_position: int | None
    included_in_time_basis: bool
    consecutive_time_delta: float | None


@dataclass(frozen=True, slots=True)
class Coverage:
    requested_laps: int
    recorded_laps: int
    missing_laps: int
    missing_times: int
    invalid_times: int
    valid_times: int
    basis_samples: int
    basis_excluded: int
    usable_positions: int
    out_of_range: int


@dataclass(frozen=True, slots=True)
class ConsecutiveRun:
    first_lap: int
    last_lap: int
    sample_count: int


@dataclass(frozen=True, slots=True)
class RollingWindow:
    first_lap: int
    last_lap: int
    sample_count: int
    mean: float
    median: float
    minimum: float
    maximum: float


@dataclass(frozen=True, slots=True)
class WindowSeries:
    size: int
    windows: tuple[RollingWindow, ...]
    best_mean: Metric


@dataclass(frozen=True, slots=True)
class PositionPoint:
    lap: int
    position: int
    source_index: int


@dataclass(frozen=True, slots=True)
class PositionProgression:
    points: tuple[PositionPoint, ...]
    gaps: tuple[LapGap, ...]
    start: PositionPoint | None
    end: PositionPoint | None
    change: Metric
    best: Metric
    worst: Metric
    first_position_samples: Metric


@dataclass(frozen=True, slots=True)
class DriverLapAnalytics:
    driver_id: int
    status: AnalyticsStatus
    reason: str | None
    samples: tuple[LapSample, ...]
    gaps: tuple[LapGap, ...]
    coverage: Coverage
    metrics: tuple[Metric, ...]
    fastest_lap: int | None
    consecutive_runs: tuple[ConsecutiveRun, ...]
    rolling: tuple[WindowSeries, ...]
    positions: PositionProgression


@dataclass(frozen=True, slots=True)
class RelativeMetric:
    name: str
    left_value: float | int | None
    right_value: float | int | None
    difference: Metric
    relative_percent: Metric


@dataclass(frozen=True, slots=True)
class DriverComparison:
    left_driver_id: int
    right_driver_id: int
    left_sample_count: int
    right_sample_count: int
    metrics: tuple[RelativeMetric, ...]


@dataclass(frozen=True, slots=True)
class ReportedMetricGroup:
    dataset: HistoryDataset
    source_index: int
    title: str | None
    metrics: tuple[ReportedMetric, ...]
    # A title is a label, not a run identity. No derived interpretation.
    classification: Literal["recorded"] = field(default="recorded", init=False)


@dataclass(frozen=True, slots=True)
class StageObservation:
    dataset: HistoryDataset
    number: int
    run_namespace: Literal["stage_run"] | None
    run_id: int | None
    position: int | None
    points: int | None
    conflict: bool = False


@dataclass(frozen=True, slots=True)
class DriverPerformance:
    driver_id: int
    result: HistoricalResult | None
    result_reason: str | None
    start_finish_position_change: Metric
    reported_position_difference: Metric
    stages: tuple[StageObservation, ...]
    reported_metrics: tuple[ReportedMetricGroup, ...]
    sessions: tuple[SessionPerformance, ...]


@dataclass(frozen=True, slots=True)
class SessionPerformance:
    weekend_run_id: int
    timing_run_id: int | None
    label: str | None
    result: HistoricalResult | None


@dataclass(frozen=True, slots=True)
class AnalyticsResult:
    query: AnalyticsQuery
    status: AnalyticsStatus
    reason: str | None
    evidence: tuple[DatasetEvidence, ...]
    drivers: tuple[DriverLapAnalytics, ...]
    comparisons: tuple[DriverComparison, ...]
    performance: tuple[DriverPerformance, ...]
    race_metrics: tuple[Metric, ...]
    caveats: tuple[str, ...]
    race_timing_run_id: int | None
    contract_version: int = field(default=1, init=False)
