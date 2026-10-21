"""Immutable reported historical facts, independent of HA and analytics."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Literal

from .scoring import PitActivity, StageClassification, StageResult


class HistoryDataset(StrEnum):
    WEEKEND = "weekend"
    LAPS = "laps"
    NOTES = "notes"
    LOOP = "loop"
    AVERAGES = "averages"
    PITS = "pits"
    STAGES = "stages"


class HistoryStatus(StrEnum):
    AVAILABLE = "available"
    EMPTY = "empty"
    NOT_PUBLISHED = "not_yet_published"
    UNVERIFIED = "unsupported_unverified"
    PARTIAL = "partial"
    NETWORK_ERROR = "network_access_failure"
    INVALID = "invalid_schema_identity"


@dataclass(frozen=True, slots=True)
class HistoricalRaceKey:
    season: int
    series_id: int
    race_id: int

    def __post_init__(self) -> None:
        if (
            type(self.season) is not int
            or not 1948 <= self.season <= 9999
            or type(self.series_id) is not int
            or self.series_id not in (1, 2, 3)
            or type(self.race_id) is not int
            or not 1 <= self.race_id <= 10**10
        ):
            raise ValueError("Invalid historical race identity")


@dataclass(frozen=True, slots=True)
class HistoricalDriver:
    """NASCAR numeric namespace, never directory Driver_ID or membership_id."""

    nascar_driver_id: int
    car_number: str | None = None
    name: str | None = None
    manufacturer: str | None = None


@dataclass(frozen=True, slots=True)
class HistoricalResult:
    driver: HistoricalDriver
    result_id: int | None = None
    results_run_id: int | None = None
    finishing_position: int | None = None
    starting_position: int | None = None
    laps_completed: int | None = None
    laps_led: int | None = None
    points_earned: int | None = None
    playoff_points_earned: int | None = None
    finishing_status: str | None = None
    disqualified: bool | None = None
    official_car_number: str | None = None
    vehicle_number: str | None = None
    team_id: int | None = None
    team_name: str | None = None
    best_lap_time: float | None = None
    best_lap_speed: float | None = None
    owner_id: int | None = None
    crew_chief_id: int | None = None


@dataclass(frozen=True, slots=True)
class HistoricalSession:
    weekend_run_id: int
    timing_run_id: int | None
    run_type_code: int | None
    name: str | None
    # Original strings: no timezone inferred from a suffix or local runtime.
    run_date: str | None
    run_date_utc: str | None
    results: tuple[HistoricalResult, ...] | None


@dataclass(frozen=True, slots=True)
class HistoricalLeader:
    start_lap: int | None
    end_lap: int | None
    car_number: str | None
    # The source supplies no driver ID; never join by car number.


@dataclass(frozen=True, slots=True)
class HistoricalCaution:
    start_lap: int | None
    end_lap: int | None
    flag_code: int | None
    reason: str | None
    comment: str | None
    beneficiary_car_number: str | None


@dataclass(frozen=True, slots=True)
class WeekendStage:
    number: int
    results: tuple[StageResult, ...]


@dataclass(frozen=True, slots=True)
class WeekendScheduleItem:
    name: str | None
    run_type_code: int | None
    start_time_utc_reported: str | None
    notes: str | None


@dataclass(frozen=True, slots=True)
class HistoricalWeekend:
    key: HistoricalRaceKey
    name: str | None
    track_id: int | None
    track_name: str | None
    timing_run_id: int | None
    scheduled_laps: int | None
    actual_laps: int | None
    scheduled_distance: float | None
    actual_distance: float | None
    date_scheduled_reported: str | None
    race_date_reported: str | None
    inspection_complete: bool | None
    results: tuple[HistoricalResult, ...] | None
    sessions: tuple[HistoricalSession, ...] | None
    leaders: tuple[HistoricalLeader, ...] | None
    cautions: tuple[HistoricalCaution, ...] | None
    stages: tuple[WeekendStage, ...] | None
    schedule: tuple[WeekendScheduleItem, ...] | None
    master_race_id: int | None = None
    race_type_code: int | None = None


@dataclass(frozen=True, slots=True)
class HistoricalLap:
    lap: int
    lap_time: float | None
    lap_speed: float | None
    running_position: int | None


@dataclass(frozen=True, slots=True)
class DriverLaps:
    driver: HistoricalDriver
    running_position: int | None
    laps: tuple[HistoricalLap, ...]


@dataclass(frozen=True, slots=True)
class HistoricalFlag:
    laps_completed: int
    flag_code: int | None


@dataclass(frozen=True, slots=True)
class HistoricalNote:
    lap: int
    note_id: int | None
    flag_code: int | None
    text: str | None
    # Namespace/association unverified for commentary; repeats are preserved.
    reported_driver_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class ReportedMetric:
    """Exact source field; units/formulas unverified. No inferred analytics."""

    field: str
    value: float | int | None
    interpretation: Literal["reported", "candidate_sentinel", "missing"] = "reported"


@dataclass(frozen=True, slots=True)
class HistoricalLoopDriver:
    nascar_driver_id: int
    metrics: tuple[ReportedMetric, ...]


@dataclass(frozen=True, slots=True)
class HistoricalLoop:
    name: str | None
    scheduled_laps: int | None
    actual_laps: int | None
    drivers: tuple[HistoricalLoopDriver, ...]


@dataclass(frozen=True, slots=True)
class HistoricalAverageDriver:
    driver: HistoricalDriver
    sponsor: str | None
    metrics: tuple[ReportedMetric, ...]


@dataclass(frozen=True, slots=True)
class HistoricalAverages:
    # Title is a label, not a verified run ID or race-session association.
    title: str | None
    drivers: tuple[HistoricalAverageDriver, ...]


@dataclass(frozen=True, slots=True)
class HistoricalPit:
    activity: PitActivity
    manufacturer: str | None
    # Preserve candidate sentinels which the shared physical parser omits.
    reported_numbers: tuple[ReportedMetric, ...]
    nascar_driver_id: None = field(default=None, init=False)


@dataclass(frozen=True, slots=True)
class HistoricalData:
    weekend: HistoricalWeekend | None = None
    laps: tuple[DriverLaps, ...] = ()
    flags: tuple[HistoricalFlag, ...] = ()
    notes: tuple[HistoricalNote, ...] = ()
    loops: tuple[HistoricalLoop, ...] = ()
    averages: tuple[HistoricalAverages, ...] = ()
    pits: tuple[HistoricalPit, ...] = ()
    stages: tuple[StageClassification, ...] = ()

    @property
    def empty(self) -> bool:
        return self.weekend is None and not any(
            (
                self.laps,
                self.flags,
                self.notes,
                self.loops,
                self.averages,
                self.pits,
                self.stages,
            )
        )


@dataclass(frozen=True, slots=True)
class HistoryProvenance:
    dataset: HistoryDataset
    requested: HistoricalRaceKey
    validation: Literal[
        "reported_identity", "path_context_only", "not_validated", "fictional"
    ]
    coverage: Literal["observed_example", "unverified_context", "fictional"]
    delivery: str
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    response_at: str | None = None
    http_status: int | None = None
    retry_after: float | None = None


@dataclass(frozen=True, slots=True)
class HistoryResult:
    status: HistoryStatus
    provenance: HistoryProvenance
    data: HistoricalData | None = None
    reason: str | None = None
    classification: Literal["reported_unverified_finality"] = field(
        default="reported_unverified_finality", init=False
    )


@dataclass(frozen=True, slots=True)
class HistoryResponse:
    """Separate datasets; no implicit cross-feed join or context borrowing."""

    key: HistoricalRaceKey
    results: tuple[HistoryResult, ...]

    @property
    def status(self) -> HistoryStatus:
        statuses = {result.status for result in self.results}
        if len(statuses) == 1:
            return next(iter(statuses))
        if statuses <= {HistoryStatus.AVAILABLE, HistoryStatus.EMPTY}:
            return HistoryStatus.AVAILABLE
        return HistoryStatus.PARTIAL

    def dataset(self, kind: HistoryDataset) -> HistoryResult | None:
        return next((r for r in self.results if r.provenance.dataset == kind), None)
