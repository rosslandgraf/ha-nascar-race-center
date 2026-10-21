"""Strict bounded adapters for observed historical profiles 13–19.

Path context is explicit provenance, never a fabricated response identity.
Unknown enum codes and candidate sentinels remain reported values.
"""

import math
import re
from collections.abc import Callable

from .history_models import (
    DriverLaps,
    HistoricalAverageDriver,
    HistoricalAverages,
    HistoricalCaution,
    HistoricalData,
    HistoricalDriver,
    HistoricalFlag,
    HistoricalLap,
    HistoricalLeader,
    HistoricalLoop,
    HistoricalLoopDriver,
    HistoricalNote,
    HistoricalPit,
    HistoricalRaceKey,
    HistoricalResult,
    HistoricalSession,
    HistoricalWeekend,
    HistoryDataset,
    ReportedMetric,
    WeekendScheduleItem,
    WeekendStage,
)
from .scoring import Provenance, StageResult, parse_pit_feed, parse_stage_feed

MAX_DRIVERS = 100
MAX_LAPS = 5000
MAX_LAP_ROWS = 50000
MAX_NOTES = 10000
MAX_PITS = 2000
MAX_SESSIONS = 30
MAX_TEXT = 2048
_DECIMAL = re.compile(r"[+-]?[0-9]+(?:\.[0-9]+)?")

LOOP_INTS = (
    "start_ps",
    "mid_ps",
    "ps",
    "closing_ps",
    "closing_laps_diff",
    "best_ps",
    "worst_ps",
    "passes_gf",
    "passing_diff",
    "passed_gf",
    "quality_passes",
    "fast_laps",
    "top15_laps",
    "lead_laps",
    "laps",
)
AVERAGE_FIELDS = (
    "OverAllAvg",
    "OverAllAvgRank",
    "BestLapTime",
    "BestLapRank",
    *(f"Con{n}Lap{suffix}" for n in (5, 10, 15, 20, 25, 30) for suffix in ("", "Rank")),
)
PIT_FLOATS = (
    "pit_in_race_time",
    "pit_out_race_time",
    "total_duration",
    "box_stop_race_time",
    "box_leave_race_time",
    "pit_stop_duration",
    "in_travel_duration",
    "out_travel_duration",
)
PIT_INTS = (
    "leader_lap",
    "lap_count",
    "pit_in_flag_status",
    "pit_out_flag_status",
    "previous_lap_time",
    "next_lap_time",
    "pit_in_rank",
    "pit_out_rank",
    "positions_gained_lost",
)


def obj(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or any(not isinstance(k, str) for k in value):
        raise ValueError("Invalid historical object")
    return value


def rows(value: object, limit: int) -> list[dict[str, object]]:
    if not isinstance(value, list) or len(value) > limit:
        raise ValueError("Invalid or oversized historical array")
    return [obj(row) for row in value]


def integer(value: object, *, required: bool = False, minimum: int = 0) -> int | None:
    if value is None and not required:
        return None
    if type(value) is not int or not minimum <= value <= 10**10:
        raise ValueError("Invalid historical integer")
    return value


def identity(value: object) -> int:
    result = integer(value, required=True, minimum=1)
    assert result is not None
    return result


def number(value: object, *, string: bool = False, minimum: float = 0) -> float | None:
    if value is None:
        return None
    if string and isinstance(value, str):
        if len(value) > 32 or _DECIMAL.fullmatch(value) is None:
            raise ValueError("Invalid historical numeric string")
        value = float(value)
    if not isinstance(value, (float, int)) or isinstance(value, bool):
        raise ValueError("Invalid historical number")
    result = float(value)
    if not math.isfinite(result) or not minimum <= result <= 10**12:
        raise ValueError("Invalid or extreme historical number")
    return result


def text(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or len(value) > MAX_TEXT:
        raise ValueError("Invalid historical text")
    return value


def boolean(value: object) -> bool | None:
    if value is not None and type(value) is not bool:
        raise ValueError("Invalid historical boolean")
    return value


def context(
    row: dict[str, object], key: HistoricalRaceKey, *, required: bool = False
) -> None:
    for field, expected in (
        ("race_id", key.race_id),
        ("series_id", key.series_id),
        ("race_season", key.season),
    ):
        if field in row or required:
            actual = identity(row.get(field))
            if actual != expected:
                raise ValueError("Conflicting historical identity")


def driver(
    row: dict[str, object], *, capitalized: bool = False, session: bool = False
) -> HistoricalDriver:
    return HistoricalDriver(
        identity(row.get("NASCARDriverID" if capitalized else "driver_id")),
        text(row.get("Number" if capitalized else "car_number")),
        text(
            row.get(
                "FullName"
                if capitalized
                else "driver_name"
                if session
                else "driver_fullname"
            )
        ),
        text(
            row.get(
                "Manufacturer"
                if capitalized
                else "manufacturer"
                if session
                else "car_make"
            )
        ),
    )


def unique_drivers(ids: list[int]) -> None:
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicate historical driver identity")


def optional_rows[T](
    row: dict[str, object], field: str, parser: Callable[[object], T]
) -> T | None:
    return None if row.get(field) is None else parser(row[field])


def results(
    value: object, key: HistoricalRaceKey, *, session: bool = False
) -> tuple[HistoricalResult, ...]:
    output = []
    for row in rows(value, MAX_DRIVERS):
        context(row, key)
        output.append(
            HistoricalResult(
                driver(row, session=session),
                integer(row.get("result_id")),
                integer(row.get("run_id")),
                integer(row.get("finishing_position")),
                integer(row.get("starting_position")),
                integer(row.get("laps_completed")),
                integer(row.get("laps_led")),
                integer(row.get("points_earned")),
                integer(row.get("playoff_points_earned")),
                text(row.get("finishing_status")),
                boolean(row.get("disqualified")),
                text(row.get("official_car_number")),
                text(row.get("vehicle_number")),
                integer(row.get("team_id")),
                text(row.get("team_name")),
                number(row.get("best_lap_time")),
                number(row.get("best_lap_speed")),
                owner_id=integer(row.get("owner_id")),
                crew_chief_id=integer(row.get("crew_chief_id")),
            )
        )
    unique_drivers([r.driver.nascar_driver_id for r in output])
    return tuple(output)


def sessions(value: object, key: HistoricalRaceKey) -> tuple[HistoricalSession, ...]:
    output = []
    for row in rows(value, MAX_SESSIONS):
        context(row, key)
        # race_id is actually reported by weekend_runs; require it.
        if identity(row.get("race_id")) != key.race_id:
            raise ValueError("Conflicting session race")
        output.append(
            HistoricalSession(
                identity(row.get("weekend_run_id")),
                integer(row.get("timing_run_id")),
                integer(row.get("run_type"), minimum=-(10**10)),
                text(row.get("run_name")),
                text(row.get("run_date")),
                text(row.get("run_date_utc")),
                optional_rows(row, "results", lambda v: results(v, key, session=True)),
            )
        )
    if len({r.weekend_run_id for r in output}) != len(output):
        raise ValueError("Duplicate weekend run identity")
    return tuple(output)


def segments(
    value: object, key: HistoricalRaceKey, *, caution: bool
) -> tuple[HistoricalLeader, ...] | tuple[HistoricalCaution, ...]:
    leaders: list[HistoricalLeader] = []
    cautions: list[HistoricalCaution] = []
    for row in rows(value, MAX_LAPS):
        context(row, key)
        start, end = integer(row.get("start_lap")), integer(row.get("end_lap"))
        if start is not None and end is not None and end < start:
            raise ValueError("Reversed historical segment")
        if caution:
            cautions.append(
                HistoricalCaution(
                    start,
                    end,
                    integer(row.get("flag_state"), minimum=-(10**10)),
                    text(row.get("reason")),
                    text(row.get("comment")),
                    text(row.get("beneficiary_car_number")),
                )
            )
        else:
            leaders.append(HistoricalLeader(start, end, text(row.get("car_number"))))
    return tuple(cautions) if caution else tuple(leaders)


def weekend_stages(value: object) -> tuple[WeekendStage, ...]:
    output = []
    for row in rows(value, 20):
        stage_results = tuple(
            StageResult(
                identity(r.get("driver_id")),
                integer(r.get("finishing_position")),
                integer(r.get("stage_points")),
                text(r.get("car_number")),
            )
            for r in rows(row.get("results"), MAX_DRIVERS)
        )
        unique_drivers([r.driver_id for r in stage_results])
        output.append(WeekendStage(identity(row.get("stage_number")), stage_results))
    if len({r.number for r in output}) != len(output):
        raise ValueError("Duplicate historical stage")
    return tuple(output)


def parse_weekend(payload: object, key: HistoricalRaceKey) -> HistoricalData:
    root = obj(payload)
    races = rows(root.get("weekend_race"), 1)
    runs = optional_rows(root, "weekend_runs", lambda v: sessions(v, key))
    if not races:
        if runs:
            raise ValueError("Weekend runs without race metadata")
        return HistoricalData()
    row = races[0]
    context(row, key, required=True)
    # Narrow the union using distinct model constructors below.
    leader_rows = optional_rows(
        row, "race_leaders", lambda v: segments(v, key, caution=False)
    )
    caution_rows = optional_rows(
        row, "caution_segments", lambda v: segments(v, key, caution=True)
    )
    return HistoricalData(
        weekend=HistoricalWeekend(
            key,
            text(row.get("race_name")),
            integer(row.get("track_id")),
            text(row.get("track_name")),
            integer(row.get("timing_run_id")),
            integer(row.get("scheduled_laps")),
            integer(row.get("actual_laps")),
            number(row.get("scheduled_distance")),
            number(row.get("actual_distance")),
            text(row.get("date_scheduled")),
            text(row.get("race_date")),
            boolean(row.get("inspection_complete")),
            optional_rows(row, "results", lambda v: results(v, key)),
            runs,
            None
            if leader_rows is None
            else tuple(r for r in leader_rows if isinstance(r, HistoricalLeader)),
            None
            if caution_rows is None
            else tuple(r for r in caution_rows if isinstance(r, HistoricalCaution)),
            optional_rows(row, "stage_results", weekend_stages),
            optional_rows(
                row,
                "schedule",
                lambda v: tuple(
                    WeekendScheduleItem(
                        text(r.get("event_name")),
                        integer(r.get("run_type"), minimum=-(10**10)),
                        text(r.get("start_time_utc")),
                        text(r.get("notes")),
                    )
                    for r in rows(v, MAX_SESSIONS)
                ),
            ),
            master_race_id=integer(row.get("master_race_id")),
            race_type_code=integer(row.get("race_type_id"), minimum=-(10**10)),
        )
    )


def parse_laps(payload: object, key: HistoricalRaceKey) -> HistoricalData:
    root = obj(payload)
    context(root, key)
    output = []
    count = 0
    for row in rows(root.get("laps"), MAX_DRIVERS):
        lap_rows = rows(row.get("Laps"), MAX_LAPS)
        count += len(lap_rows)
        if count > MAX_LAP_ROWS:
            raise ValueError("Historical lap budget exceeded")
        laps = tuple(
            HistoricalLap(
                integer_required(r.get("Lap")),
                number(r.get("LapTime")),
                number(r.get("LapSpeed"), string=True),
                integer(r.get("RunningPos")),
            )
            for r in lap_rows
        )
        if len({r.lap for r in laps}) != len(laps):
            raise ValueError("Duplicate driver lap")
        output.append(
            DriverLaps(
                driver(row, capitalized=True), integer(row.get("RunningPos")), laps
            )
        )
    unique_drivers([r.driver.nascar_driver_id for r in output])
    flags = tuple(
        HistoricalFlag(
            integer_required(r.get("LapsCompleted")),
            integer(r.get("FlagState"), minimum=-(10**10)),
        )
        for r in rows(root.get("flags"), MAX_LAPS)
    )
    return HistoricalData(laps=tuple(output), flags=flags)


def integer_required(value: object) -> int:
    result = integer(value, required=True)
    assert result is not None
    return result


def parse_notes(payload: object, key: HistoricalRaceKey) -> HistoricalData:
    root = obj(payload)
    context(root, key)
    laps = obj(root.get("laps"))
    if len(laps) > MAX_LAPS:
        raise ValueError("Historical note lap budget exceeded")
    output: list[HistoricalNote] = []
    for lap, value in laps.items():
        if (
            len(lap) > 5
            or not lap.isascii()
            or not lap.isdecimal()
            or str(int(lap)) != lap
        ):
            raise ValueError("Invalid historical note lap key")
        for row in rows(value, MAX_NOTES):
            if len(output) >= MAX_NOTES:
                raise ValueError("Historical note budget exceeded")
            ids = row.get("DriverIDs")
            if not isinstance(ids, list) or len(ids) > MAX_DRIVERS:
                raise ValueError("Invalid commentary driver IDs")
            output.append(
                HistoricalNote(
                    int(lap),
                    integer(row.get("NoteID")),
                    integer(row.get("FlagState"), minimum=-(10**10)),
                    text(row.get("Note")),
                    tuple(identity(v) for v in ids),
                )
            )
    return HistoricalData(notes=tuple(output))


def metric(
    row: dict[str, object],
    field: str,
    *,
    integral: bool = False,
    sentinel: bool = False,
) -> ReportedMetric:
    value = (
        integer(row.get(field), minimum=-(10**10))
        if integral
        else number(row.get(field), minimum=-(10**12))
    )
    return ReportedMetric(
        field,
        value,
        "missing"
        if value is None
        else "candidate_sentinel"
        if sentinel and value in (-1, 0, 999)
        else "reported",
    )


def parse_loop(payload: object, key: HistoricalRaceKey) -> HistoricalData:
    output = []
    for row in rows(payload, 1):
        context(row, key)
        if (
            identity(row.get("race_id")) != key.race_id
            or identity(row.get("series_id")) != key.series_id
        ):
            raise ValueError("Conflicting loop identity")
        drivers = tuple(
            HistoricalLoopDriver(
                identity(r.get("driver_id")),
                tuple(
                    metric(r, f, integral=f in LOOP_INTS)
                    for f in (*LOOP_INTS, "avg_ps", "rating")
                ),
            )
            for r in rows(row.get("drivers"), MAX_DRIVERS)
        )
        unique_drivers([r.nascar_driver_id for r in drivers])
        output.append(
            HistoricalLoop(
                text(row.get("race_name")),
                integer(row.get("sch_laps")),
                integer(row.get("act_laps")),
                drivers,
            )
        )
    return HistoricalData(loops=tuple(output))


def parse_averages(payload: object, key: HistoricalRaceKey) -> HistoricalData:
    output = []
    for row in rows(payload, MAX_SESSIONS):
        context(row, key)
        drivers = tuple(
            HistoricalAverageDriver(
                driver(r, capitalized=True),
                text(r.get("Sponsor")),
                tuple(
                    metric(r, f, integral=f.endswith("Rank"), sentinel=True)
                    for f in AVERAGE_FIELDS
                ),
            )
            for r in rows(row.get("Items"), MAX_DRIVERS)
        )
        unique_drivers([r.driver.nascar_driver_id for r in drivers])
        output.append(HistoricalAverages(text(row.get("Title")), drivers))
    return HistoricalData(averages=tuple(output))


def parse_pits(payload: object, key: HistoricalRaceKey) -> HistoricalData:
    source = rows(payload, MAX_PITS)
    observations = []
    for row in source:
        context(row, key)
        for field in (
            "vehicle_number",
            "driver_name",
            "vehicle_manufacturer",
            "pit_stop_type",
        ):
            text(row.get(field))
        for tire in ("left_front", "left_rear", "right_front", "right_rear"):
            boolean(row.get(f"{tire}_tire_changed"))
        observations.append(
            tuple(
                metric(
                    row,
                    f,
                    integral=f in PIT_INTS,
                    sentinel=f != "positions_gained_lost",
                )
                for f in (*PIT_FLOATS, *PIT_INTS)
            )
        )
    # Reuse Phase 3B unchanged: no weaker physical/association validation.
    parsed = parse_pit_feed(payload, Provenance("archived_pits", "historical"))
    return HistoricalData(
        pits=tuple(
            HistoricalPit(activity, text(row.get("vehicle_manufacturer")), raw)
            for row, activity, raw in zip(
                source, parsed.pits, observations, strict=True
            )
        )
    )


def parse_stages(payload: object, key: HistoricalRaceKey) -> HistoricalData:
    for row in rows(payload, 20):
        context(row, key)
        if identity(row.get("race_id")) != key.race_id:
            raise ValueError("Conflicting archived stage race")
        identity(row.get("run_id"))
        identity(row.get("stage_number"))
        for result in rows(row.get("results"), MAX_DRIVERS):
            identity(result.get("driver_id"))
            integer(result.get("position"))
            integer(result.get("stage_points"))
            text(result.get("vehicle_number"))
    # Keep the stage_run namespace; a matching integer is not a timing-run join.
    parsed = parse_stage_feed(payload, Provenance("archived_stages", "historical"))
    if len({s.context.run_id for s in parsed.stages}) > 1:
        raise ValueError("Conflicting archived stage runs")
    return HistoricalData(stages=parsed.stages)


PARSERS: dict[HistoryDataset, Callable[[object, HistoricalRaceKey], HistoricalData]] = {
    HistoryDataset.WEEKEND: parse_weekend,
    HistoryDataset.LAPS: parse_laps,
    HistoryDataset.NOTES: parse_notes,
    HistoryDataset.LOOP: parse_loop,
    HistoryDataset.AVERAGES: parse_averages,
    HistoryDataset.PITS: parse_pits,
    HistoryDataset.STAGES: parse_stages,
}
