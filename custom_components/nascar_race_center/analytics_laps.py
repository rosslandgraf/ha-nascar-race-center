"""Pure deterministic recorded-lap calculations. See docs/ANALYTICS.md."""

import math
from collections.abc import Iterable
from statistics import median, pstdev

from .analytics_models import (
    AnalyticsQuery,
    AnalyticsStatus,
    ConsecutiveRun,
    Coverage,
    DriverLapAnalytics,
    LapGap,
    LapSample,
    Metric,
    PositionPoint,
    PositionProgression,
    RollingWindow,
    WindowSeries,
)
from .analytics_validation import position, valid_time
from .history_models import DriverLaps

TIME_UNIT = "source_lap_time_unit_unverified"


def metric(
    name: str,
    value: float | int | None,
    method: str,
    unit: str = TIME_UNIT,
    reason: str | None = None,
) -> Metric:
    if value is not None and not math.isfinite(value):
        value, reason = None, "numerical_range"
    return Metric(name, value, method, unit, reason=reason if value is None else None)


def mean(values: list[float]) -> float:
    try:
        return math.fsum(values) / len(values)
    except OverflowError:
        scale = max(values)
        return (math.fsum(v / scale for v in values) / len(values)) * scale


def time_metrics(values: list[float], deltas: list[float]) -> tuple[Metric, ...]:
    count = len(values)
    average = mean(values) if values else None
    med = float(median(values)) if values else None
    # statistics.median can overflow on two extreme positive values.
    if med is not None and not math.isfinite(med):
        ordered = sorted(values)
        med = mean(ordered[(count - 1) // 2 : count // 2 + 1])
    deviation = coefficient = None
    if count >= 2:
        deviation = pstdev(values)
        assert average is not None
        coefficient = deviation / average
    missing = "no_valid_lap_times"
    small = "requires_two_valid_laps"
    return (
        metric(
            "fastest_reported_lap",
            min(values) if values else None,
            "minimum",
            reason=missing,
        ),
        metric("mean", average, "arithmetic_mean", reason=missing),
        metric("median", med, "median", reason=missing),
        metric("minimum", min(values) if values else None, "minimum", reason=missing),
        metric("maximum", max(values) if values else None, "maximum", reason=missing),
        metric(
            "range",
            max(values) - min(values) if values else None,
            "maximum_minus_minimum",
            reason=missing,
        ),
        metric(
            "population_stddev",
            deviation,
            "population_standard_deviation",
            reason=small,
        ),
        metric(
            "coefficient_of_variation",
            coefficient,
            "population_stddev_divided_by_mean",
            "dimensionless",
            small,
        ),
        metric(
            "mean_absolute_consecutive_change",
            mean([abs(d) for d in deltas]) if deltas else None,
            "mean_absolute_difference_of_adjacent_numbered_valid_laps",
            reason="no_consecutive_valid_pair",
        ),
        metric("consecutive_pair_count", len(deltas), "count", "count"),
    )


def gaps(laps: Iterable[int], query: AnalyticsQuery) -> tuple[LapGap, ...]:
    """Compress absence into intervals, never allocate invented lap samples."""
    output: list[LapGap] = []
    cursor = query.first_lap
    for lap in sorted(laps):
        if lap > cursor:
            output.append(LapGap(cursor, lap - 1))
        cursor = lap + 1
    if cursor <= query.last_lap:
        output.append(LapGap(cursor, query.last_lap))
    return tuple(output)


def position_progression(
    samples: tuple[LapSample, ...], query: AnalyticsQuery
) -> PositionProgression:
    points = tuple(
        sorted(
            (
                PositionPoint(s.lap, s.usable_position, s.source_index)
                for s in samples
                if s.usable_position is not None
            ),
            key=lambda p: p.lap,
        )
    )
    start, end = (points[0], points[-1]) if points else (None, None)
    change = (
        start.position - end.position if start and end and len(points) >= 2 else None
    )
    return PositionProgression(
        points,
        gaps((p.lap for p in points), query),
        start,
        end,
        metric(
            "observed_position_change",
            change,
            "first_position_minus_last_position",
            "position",
            "requires_two_observed_positions",
        ),
        metric(
            "best_observed_position",
            min(p.position for p in points) if points else None,
            "minimum",
            "position",
            "no_usable_positions",
        ),
        metric(
            "worst_observed_position",
            max(p.position for p in points) if points else None,
            "maximum",
            "position",
            "no_usable_positions",
        ),
        metric(
            "first_position_observation_count",
            sum(p.position == 1 for p in points) if points else None,
            "count_of_observations_at_position_one",
            "count",
            "no_usable_positions",
        ),
    )


def lap_analytics(
    source: DriverLaps | None,
    driver_id: int,
    query: AnalyticsQuery,
    common_laps: set[int] | None,
    unavailable_reason: str | None,
) -> DriverLapAnalytics:
    recorded = (
        [
            (i, lap)
            for i, lap in enumerate(source.laps)
            if query.first_lap <= lap.lap <= query.last_lap
        ]
        if source
        else []
    )
    values_by_lap = {
        lap.lap: float(lap.lap_time)
        for _, lap in recorded
        if valid_time(lap.lap_time)
        and (common_laps is None or lap.lap in common_laps)
        and lap.lap_time is not None
    }
    samples = tuple(
        LapSample(
            lap.lap,
            i,
            float(lap.lap_time)
            if isinstance(lap.lap_time, (int, float))
            and not isinstance(lap.lap_time, bool)
            and math.isfinite(lap.lap_time)
            else None,
            lap.running_position,
            valid_time(lap.lap_time),
            None
            if valid_time(lap.lap_time)
            else "missing"
            if lap.lap_time is None
            else "invalid_nonpositive_or_nonfinite",
            position(lap.running_position),
            lap.lap in values_by_lap,
            values_by_lap[lap.lap] - values_by_lap[lap.lap - 1]
            if lap.lap in values_by_lap and lap.lap - 1 in values_by_lap
            else None,
        )
        for i, lap in recorded
    )
    ordered = sorted(values_by_lap)
    runs: list[ConsecutiveRun] = []
    for lap in ordered:
        if runs and runs[-1].last_lap + 1 == lap:
            prior = runs[-1]
            runs[-1] = ConsecutiveRun(prior.first_lap, lap, prior.sample_count + 1)
        else:
            runs.append(ConsecutiveRun(lap, lap, 1))
    rolling: list[WindowSeries] = []
    for size in query.windows:
        windows: list[RollingWindow] = []
        for run in runs:
            for first in range(run.first_lap, run.last_lap - size + 2):
                values = [values_by_lap[n] for n in range(first, first + size)]
                ordered_values = sorted(values)
                mid = size // 2
                med = (
                    ordered_values[mid]
                    if size % 2
                    else mean(ordered_values[mid - 1 : mid + 1])
                )
                windows.append(
                    RollingWindow(
                        first,
                        first + size - 1,
                        size,
                        mean(values),
                        med,
                        min(values),
                        max(values),
                    )
                )
        rolling.append(
            WindowSeries(
                size,
                tuple(windows),
                metric(
                    f"best_{size}_lap_mean",
                    min(w.mean for w in windows) if windows else None,
                    "minimum_mean_of_valid_consecutively_numbered_windows",
                    reason="no_sufficient_contiguous_window",
                ),
            )
        )
    valid_count = sum(s.valid_time for s in samples)
    missing_count = sum(s.time_exclusion == "missing" for s in samples)
    positions = position_progression(samples, query)
    reason = unavailable_reason or (
        "driver_not_recorded"
        if source is None
        else "no_observations_in_range"
        if not samples
        else None
    )
    status = AnalyticsStatus.UNAVAILABLE if reason else AnalyticsStatus.AVAILABLE
    if reason is None and (
        valid_count != len(samples)
        or len(positions.points) != len(samples)
        or len(values_by_lap) != valid_count
        or len(samples) != query.last_lap - query.first_lap + 1
    ):
        status = AnalyticsStatus.PARTIAL
    values = [values_by_lap[n] for n in ordered]
    metrics = time_metrics(
        values,
        [
            s.consecutive_time_delta
            for s in samples
            if s.consecutive_time_delta is not None
        ],
    )
    return DriverLapAnalytics(
        driver_id,
        status,
        reason,
        samples,
        gaps((s.lap for s in samples), query),
        Coverage(
            query.last_lap - query.first_lap + 1,
            len(samples),
            query.last_lap - query.first_lap + 1 - len(samples),
            missing_count,
            len(samples) - valid_count - missing_count,
            valid_count,
            len(values_by_lap),
            valid_count - len(values_by_lap),
            len(positions.points),
            len(source.laps) - len(samples) if source else 0,
        ),
        metrics,
        min(ordered, key=lambda n: (values_by_lap[n], n)) if ordered else None,
        tuple(runs),
        tuple(rolling),
        positions,
    )
