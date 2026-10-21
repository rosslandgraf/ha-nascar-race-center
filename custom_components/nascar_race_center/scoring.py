"""Evidence-limited immutable pit, stage and points facts.

See docs/PHASE3B_EVIDENCE.md. No network, inferred scores, time units or finality.
Standalone context is never borrowed from the global leaderboard.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Literal

from .timing import _count, _number, _text


def _signed(value: object) -> int | None:
    if isinstance(value, str) and len(value) <= 21:
        try:
            value = int(value)
        except ValueError:
            return None
    return value if type(value) is int and abs(value) <= 10**20 else None


def _physical(value: object) -> float | None:
    # Zero and negative values occur in placeholders/incomplete records. Neither
    # is evidence of a physical stop duration, nor of a completed pit stop.
    return _number(value, positive=True)


def _boolean(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


@dataclass(frozen=True, slots=True)
class RaceContext:
    """IDs retain their namespace; zero/missing IDs are unknown, never wildcards."""

    series_id: int | None = None
    race_id: int | None = None
    run_id: int | None = None
    run_namespace: str | None = None
    season: int | None = None


@dataclass(frozen=True, slots=True)
class Provenance:
    """Content time and transport time are deliberately independent."""

    endpoint: str
    scope: Literal["global", "embedded", "historical", "synthetic"] = "global"
    source_updated_at: datetime | None = None
    retrieved_at: datetime = field(
        default_factory=lambda: datetime.now(UTC), compare=False
    )


@dataclass(frozen=True, slots=True)
class PitStop:
    """One embedded observation, owned by its parent NASCAR driver identity.

    Clocks are reported values with unverified units. No completion/count or
    duration is derived from them. Signed movement is a reported source fact.
    """

    lap: int | None = None
    leader_lap: int | None = None
    entry_time: float | None = None
    exit_time: float | None = None
    entry_position: int | None = None
    exit_position: int | None = None
    position_change: int | None = None


def parse_embedded_pits(payload: object) -> tuple[PitStop, ...]:
    rows = _rows(payload, 1000)
    return tuple(
        PitStop(
            lap=_count(row.get("pit_in_lap_count"), positive=True),
            leader_lap=_count(row.get("pit_in_leader_lap"), positive=True),
            entry_time=_physical(row.get("pit_in_elapsed_time")),
            exit_time=_physical(row.get("pit_out_elapsed_time")),
            entry_position=_count(row.get("pit_in_rank"), positive=True),
            exit_position=_count(row.get("pit_out_rank"), positive=True),
            position_change=_signed(row.get("positions_gained_lossed")),
        )
        for row in rows
    )


def latest_pit(stops: tuple[PitStop, ...] | None) -> PitStop | None:
    """Select by reported lap only; unresolved same-lap stops stay ambiguous."""
    if not stops or any(stop.lap is None for stop in stops):
        return None
    latest = max(stop.lap for stop in stops if stop.lap is not None)
    candidates = {stop for stop in stops if stop.lap == latest}
    return next(iter(candidates)) if len(candidates) == 1 else None


@dataclass(frozen=True, slots=True)
class CurrentStage:
    """Reported stage descriptor; no completed stages inferred from its number."""

    number: int | None
    finish_at_lap: int | None
    laps_in_stage: int | None


def parse_current_stage(payload: object) -> CurrentStage:
    if not isinstance(payload, dict):
        raise ValueError("Invalid stage descriptor")
    return CurrentStage(
        _count(payload.get("stage_num"), positive=True),
        _count(payload.get("finish_at_lap"), positive=True),
        _count(payload.get("laps_in_stage"), positive=True),
    )


@dataclass(frozen=True, slots=True)
class PitActivity:
    """Standalone pit row without invented driver identity or race context."""

    car_number: str | None
    driver_name: str | None
    stop: PitStop
    stop_type: str | None
    total_duration: float | None
    stop_duration: float | None
    box_stop_time: float | None
    box_leave_time: float | None
    in_travel_duration: float | None
    out_travel_duration: float | None
    entry_flag_code: int | None
    exit_flag_code: int | None
    # LF, LR, RF, RR; actual bools only. False is a reported fact, not missing.
    tires_changed: tuple[bool | None, ...]


@dataclass(frozen=True, slots=True)
class StageResult:
    driver_id: int
    position: int | None
    points: int | None
    car_number: str | None = None


@dataclass(frozen=True, slots=True)
class StageClassification:
    context: RaceContext
    number: int
    results: tuple[StageResult, ...]

    def driver(self, driver_id: int) -> StageResult | None:
        return next((row for row in self.results if row.driver_id == driver_id), None)


@dataclass(frozen=True, slots=True)
class DriverPoints:
    context: RaceContext
    driver_id: int
    membership_id: int | None
    position: int | None
    points: int | None
    race_points: int | None
    bonus_points: int | None
    stage_points: tuple[int | None, ...]
    stage_winner: tuple[bool | None, ...]
    delta_leader: int | None
    delta_next: int | None
    eligible: bool | None
    wins: int | None
    top_five: int | None
    top_ten: int | None
    poles: int | None
    fastest_lap_point: bool | None


@dataclass(frozen=True, slots=True)
class ScoringFeed:
    """One whole feed snapshot. Never merged with older successful rows."""

    kind: Literal["pits", "stages", "points"]
    provenance: Provenance
    contexts: tuple[RaceContext, ...] = ()
    pits: tuple[PitActivity, ...] = ()
    stages: tuple[StageClassification, ...] = ()
    points: tuple[DriverPoints, ...] = ()
    # These feeds do not establish official results, including after checkered.
    classification: Literal["provisional"] = field(default="provisional", init=False)

    def driver_points(self, driver_id: int) -> DriverPoints | None:
        rows = [row for row in self.points if row.driver_id == driver_id]
        return rows[0] if len(rows) == 1 else None


def _rows(payload: object, limit: int) -> list[dict[str, object]]:
    if not isinstance(payload, list) or len(payload) > limit:
        raise ValueError("Invalid scoring array")
    if any(not isinstance(row, dict) for row in payload):
        raise ValueError("Invalid scoring row")
    return payload


def _identity(row: dict[str, object]) -> int:
    identity = _count(row.get("driver_id"), positive=True)
    if identity is None:
        raise ValueError("Scoring row has no NASCAR driver ID")
    return identity


def parse_pit_feed(payload: object, provenance: Provenance) -> ScoringFeed:
    """03/18/23 share structural fields, but no global race/driver IDs."""
    pits = tuple(
        PitActivity(
            car_number=_text(row.get("vehicle_number")),
            driver_name=_text(row.get("driver_name")),
            stop=PitStop(
                _count(row.get("lap_count"), positive=True),
                _count(row.get("leader_lap"), positive=True),
                _physical(row.get("pit_in_race_time")),
                _physical(row.get("pit_out_race_time")),
                _count(row.get("pit_in_rank"), positive=True),
                _count(row.get("pit_out_rank"), positive=True),
                _signed(row.get("positions_gained_lost")),
            ),
            stop_type=_text(row.get("pit_stop_type")),
            total_duration=_physical(row.get("total_duration")),
            stop_duration=_physical(row.get("pit_stop_duration")),
            box_stop_time=_physical(row.get("box_stop_race_time")),
            box_leave_time=_physical(row.get("box_leave_race_time")),
            in_travel_duration=_physical(row.get("in_travel_duration")),
            out_travel_duration=_physical(row.get("out_travel_duration")),
            entry_flag_code=_count(row.get("pit_in_flag_status")),
            exit_flag_code=_count(row.get("pit_out_flag_status")),
            tires_changed=tuple(
                _boolean(row.get(f"{tire}_tire_changed"))
                for tire in ("left_front", "left_rear", "right_front", "right_rear")
            ),
        )
        for row in _rows(payload, 10000)
    )
    return ScoringFeed("pits", provenance, pits=pits)


def parse_stage_feed(payload: object, provenance: Provenance) -> ScoringFeed:
    """05/19: preserve their run namespace; no undocumented series/time fields."""
    stages: list[StageClassification] = []
    seen: set[tuple[RaceContext, int]] = set()
    for row in _rows(payload, 20):
        context = RaceContext(
            race_id=_count(row.get("race_id"), positive=True),
            run_id=_count(row.get("run_id"), positive=True),
            run_namespace="stage_run",
        )
        number = _count(row.get("stage_number"), positive=True)
        if number is None or (context, number) in seen:
            raise ValueError("Invalid or duplicate stage identity")
        seen.add((context, number))
        results = tuple(
            StageResult(
                _identity(result),
                _count(result.get("position"), positive=True),
                _count(result.get("stage_points")),
                _text(result.get("vehicle_number")),
            )
            for result in _rows(row.get("results"), 100)
        )
        if len({result.driver_id for result in results}) != len(results):
            raise ValueError("Duplicate stage driver identity")
        stages.append(StageClassification(context, number, results))
    return ScoringFeed(
        "stages",
        provenance,
        tuple(dict.fromkeys(s.context for s in stages)),
        stages=tuple(sorted(stages, key=lambda stage: stage.number)),
    )


def parse_points_feed(payload: object, provenance: Provenance) -> ScoringFeed:
    """04/22: zero IDs stay unknown; no membership-ID or scoring-rule fallback."""
    points: list[DriverPoints] = []
    seen: set[tuple[RaceContext, int]] = set()
    for row in _rows(payload, 200):
        series = _count(row.get("series_id"), positive=True)
        context = RaceContext(
            series if series in (1, 2, 3) else None,
            _count(row.get("race_id"), positive=True),
            _count(row.get("run_id"), positive=True),
            "points_run",
        )
        identity = _identity(row)
        if (context, identity) in seen:
            raise ValueError("Duplicate points driver identity")
        seen.add((context, identity))
        points.append(
            DriverPoints(
                context,
                identity,
                _count(row.get("membership_id"), positive=True),
                _count(row.get("points_position"), positive=True),
                _count(row.get("points")),
                _count(row.get("points_earned_this_race")),
                _count(row.get("bonus_points")),
                tuple(_count(row.get(f"stage_{n}_points")) for n in (1, 2, 3)),
                tuple(_boolean(row.get(f"stage_{n}_winner")) for n in (1, 2, 3)),
                _signed(row.get("delta_leader")),
                _signed(row.get("delta_next")),
                _boolean(row.get("is_points_eligible")),
                _count(row.get("wins")),
                _count(row.get("top_5")),
                _count(row.get("top_10")),
                _count(row.get("poles")),
                _boolean(row.get("is_fastest_lap_point")),
            )
        )
    return ScoringFeed(
        "points",
        provenance,
        tuple(dict.fromkeys(p.context for p in points)),
        points=tuple(points),
    )


def association_state(feed: ScoringFeed, active: RaceContext, now: datetime) -> str:
    """Require complete identity, comparable run namespaces and content freshness.

    A successful HTTP GET, identical car/driver list, matching numeric IDs in
    different namespaces, or a fresh leaderboard cannot certify another feed.
    """
    if feed.provenance.scope == "historical":
        return "historical"
    if len(feed.contexts) > 1:
        return "conflicting_context"
    context = feed.contexts[0] if feed.contexts else RaceContext()
    for key in ("series_id", "race_id", "season"):
        supplied, expected = getattr(context, key), getattr(active, key)
        if supplied is not None and expected is not None and supplied != expected:
            return "context_mismatch"
    if any(
        type(getattr(context, key)) is not int
        or getattr(context, key) <= 0
        or type(getattr(active, key)) is not int
        or getattr(active, key) <= 0
        for key in ("series_id", "race_id", "run_id")
    ):
        return "context_unknown"
    if not context.run_namespace or context.run_namespace != active.run_namespace:
        return "namespace_unverified"
    if context.run_id != active.run_id:
        return "context_mismatch"
    clock = feed.provenance.source_updated_at
    if clock is None or clock.utcoffset() is None:
        return "freshness_unknown"
    age = now - clock
    if age < -timedelta(minutes=5):
        return "freshness_unknown"
    if age > timedelta(minutes=15):
        return "stale"
    return "available"
