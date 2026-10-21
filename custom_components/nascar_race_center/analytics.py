"""Pure analytics entry point over immutable Phase 4A history observations."""

from dataclasses import replace
from itertools import combinations

from .analytics_laps import lap_analytics, metric
from .analytics_models import (
    AnalyticsQuery,
    AnalyticsResult,
    AnalyticsStatus,
    DriverComparison,
    DriverLapAnalytics,
    DriverPerformance,
    Metric,
    RelativeMetric,
    ReportedMetricGroup,
    SessionPerformance,
    StageObservation,
)
from .analytics_validation import align_history, position, valid_time
from .history_models import (
    HistoricalData,
    HistoryDataset,
    HistoryResponse,
    HistoryStatus,
)

CAVEATS = (
    "source_lap_time_and_speed_units_unverified",
    "recorded_samples_only_no_interpolation_or_condition_filter",
    "path_context_does_not_certify_lap_or_average_content_identity",
    "positions_are_observations_not_on_track_passes_or_official_laps_led",
    "reported_results_do_not_establish_official_final_classification",
    "reported_loop_and_average_formulas_unverified_no_rating_reconstruction",
    "no_tire_age_pit_cycle_fuel_or_strategy_inference",
    "archived_pits_remain_race_scoped_without_validated_driver_identity",
    "coverage_is_selected_lap_range_not_race_completion",
)


def unavailable_result(query: AnalyticsQuery, reason: str) -> AnalyticsResult:
    """Bounded broker rejection; no observations were retrieved or calculated."""
    return AnalyticsResult(
        query, AnalyticsStatus.UNAVAILABLE, reason, (), (), (), (), (), CAVEATS, None
    )


def _comparisons(
    drivers: tuple[DriverLapAnalytics, ...],
) -> tuple[DriverComparison, ...]:
    output = []
    for left, right in combinations(drivers, 2):
        left_metrics = (*left.metrics[:-1], *(r.best_mean for r in left.rolling))
        right_metrics = {
            m.name: m for m in (*right.metrics, *(r.best_mean for r in right.rolling))
        }
        metrics: list[RelativeMetric] = []
        for lhs in left_metrics:
            rhs = right_metrics[lhs.name]
            difference = (
                lhs.value - rhs.value
                if lhs.value is not None and rhs.value is not None
                else None
            )
            relative = (
                (difference / rhs.value) * 100
                if difference is not None and rhs.value not in (None, 0)
                else None
            )
            metrics.append(
                RelativeMetric(
                    lhs.name,
                    lhs.value,
                    rhs.value,
                    metric(
                        lhs.name + "_difference",
                        difference,
                        "left_minus_right",
                        lhs.unit,
                        "metric_unavailable",
                    ),
                    metric(
                        lhs.name + "_relative_percent",
                        relative,
                        "100_times_left_minus_right_divided_by_right",
                        "percent",
                        "zero_reference_value"
                        if rhs.value == 0
                        else "metric_unavailable",
                    ),
                )
            )
        output.append(
            DriverComparison(
                left.driver_id,
                right.driver_id,
                left.coverage.basis_samples,
                right.coverage.basis_samples,
                tuple(metrics),
            )
        )
    return tuple(output)


def _performance(
    driver_id: int, data: dict[HistoryDataset, HistoricalData]
) -> DriverPerformance:
    weekend_data = data.get(HistoryDataset.WEEKEND)
    weekend = weekend_data.weekend if weekend_data else None
    result = (
        next(
            (
                r
                for r in weekend.results or ()
                if r.driver.nascar_driver_id == driver_id
            ),
            None,
        )
        if weekend
        else None
    )
    start = position(result.starting_position) if result else None
    finish = position(result.finishing_position) if result else None
    stages: list[StageObservation] = []
    if weekend:
        for stage in weekend.stages or ():
            for row in stage.results:
                if row.driver_id == driver_id:
                    stages.append(
                        StageObservation(
                            HistoryDataset.WEEKEND,
                            stage.number,
                            None,
                            None,
                            row.position,
                            row.points,
                        )
                    )
    for archived_stage in data.get(HistoryDataset.STAGES, HistoricalData()).stages:
        for row in archived_stage.results:
            if row.driver_id == driver_id:
                stages.append(
                    StageObservation(
                        HistoryDataset.STAGES,
                        archived_stage.number,
                        "stage_run",
                        archived_stage.context.run_id,
                        row.position,
                        row.points,
                    )
                )
    # Do not select a winner between contradictory stage sources or merge them.
    stages = [
        replace(
            s,
            conflict=any(
                s.number == other.number
                and s.dataset != other.dataset
                and (
                    (
                        s.position is not None
                        and other.position is not None
                        and s.position != other.position
                    )
                    or (
                        s.points is not None
                        and other.points is not None
                        and s.points != other.points
                    )
                )
                for other in stages
            ),
        )
        for s in stages
    ]
    groups: list[ReportedMetricGroup] = []
    for i, loop in enumerate(data.get(HistoryDataset.LOOP, HistoricalData()).loops):
        for driver in loop.drivers:
            if driver.nascar_driver_id == driver_id:
                groups.append(
                    ReportedMetricGroup(
                        HistoryDataset.LOOP, i, loop.name, driver.metrics
                    )
                )
    for i, averages in enumerate(
        data.get(HistoryDataset.AVERAGES, HistoricalData()).averages
    ):
        for row_average in averages.drivers:
            if row_average.driver.nascar_driver_id == driver_id:
                groups.append(
                    ReportedMetricGroup(
                        HistoryDataset.AVERAGES, i, averages.title, row_average.metrics
                    )
                )
    return DriverPerformance(
        driver_id,
        result,
        None
        if result
        else "results_not_available"
        if weekend is None or weekend.results is None
        else "driver_not_in_reported_results",
        metric(
            "start_finish_position_change",
            start - finish if start is not None and finish is not None else None,
            "reported_starting_position_minus_reported_finishing_position",
            "position",
            "two_usable_reported_positions_required",
        ),
        Metric(
            "reported_position_difference",
            None,
            "source_field_not_present",
            "position",
            "recorded",
            "source_does_not_report_position_difference",
        ),
        tuple(stages),
        tuple(groups),
        tuple(
            SessionPerformance(
                session.weekend_run_id,
                session.timing_run_id,
                session.name,
                next(
                    (
                        r
                        for r in session.results or ()
                        if r.driver.nascar_driver_id == driver_id
                    ),
                    None,
                ),
            )
            for session in (weekend.sessions or () if weekend else ())
        ),
    )


def _race_metrics(data: dict[HistoryDataset, HistoricalData]) -> tuple[Metric, ...]:
    weekend_data = data.get(HistoryDataset.WEEKEND)
    weekend = weekend_data.weekend if weekend_data else None
    return tuple(
        Metric(
            field,
            getattr(weekend, field) if weekend else None,
            "reported_weekend_field",
            "count",
            "recorded",
            None
            if weekend and getattr(weekend, field) is not None
            else "reported_field_unavailable",
        )
        for field in ("scheduled_laps", "actual_laps")
    )


def analyze_history(
    response: HistoryResponse, query: AnalyticsQuery
) -> AnalyticsResult:
    """Calculate contract v1. No clocks, mutation, I/O or HA dependencies.

    Caller selects all-available or common valid recorded lap numbers for time
    comparisons; positions always use every usable observed position in range.
    """
    data, evidence = align_history(response, query)
    laps = data.get(HistoryDataset.LAPS, HistoricalData()).laps
    lookup = {d.driver.nascar_driver_id: d for d in laps}
    common: set[int] | None = None
    if query.time_basis == "overlapping_valid_laps":
        for driver_id in query.driver_ids:
            source = lookup.get(driver_id)
            valid = (
                {
                    s.lap
                    for s in source.laps
                    if query.first_lap <= s.lap <= query.last_lap
                    and valid_time(s.lap_time)
                }
                if source
                else set()
            )
            common = valid if common is None else common & valid
    lap_evidence = next((e for e in evidence if e.dataset == HistoryDataset.LAPS), None)
    lap_reason = (
        None
        if HistoryDataset.LAPS in data
        else (
            lap_evidence.reason or lap_evidence.status.value
            if lap_evidence
            else "dataset_not_requested"
        )
    )
    drivers = tuple(
        lap_analytics(lookup.get(d), d, query, common, lap_reason)
        for d in query.driver_ids
    )
    performance = tuple(_performance(d, data) for d in query.driver_ids)
    supported = {
        HistoryDataset.LAPS,
        HistoryDataset.WEEKEND,
        HistoryDataset.STAGES,
        HistoryDataset.LOOP,
        HistoryDataset.AVERAGES,
    }
    usable = bool(set(data) & supported)
    has_values = (
        any(d.samples for d in drivers)
        or any(
            p.result
            or p.stages
            or p.reported_metrics
            or any(s.result for s in p.sessions)
            for p in performance
        )
        or any(m.available for m in _race_metrics(data))
    )
    invalid = any(e.status == HistoryStatus.INVALID for e in evidence)
    failed = any(
        e.status not in (HistoryStatus.AVAILABLE, HistoryStatus.EMPTY) for e in evidence
    )
    conflicts = any(s.conflict for p in performance for s in p.stages)
    status = AnalyticsStatus.AVAILABLE
    reason = None
    if not usable or not has_values:
        status = AnalyticsStatus.INVALID if invalid else AnalyticsStatus.UNAVAILABLE
        reason = "no_usable_analytics_observations"
    elif (
        failed
        or conflicts
        or (
            lap_evidence is not None
            and any(d.status != AnalyticsStatus.AVAILABLE for d in drivers)
        )
    ):
        status = AnalyticsStatus.PARTIAL
    weekend_data = data.get(HistoryDataset.WEEKEND)
    return AnalyticsResult(
        query,
        status,
        reason,
        evidence,
        drivers,
        _comparisons(drivers),
        performance,
        _race_metrics(data),
        CAVEATS + (("conflicting_reported_stage_observations",) if conflicts else ()),
        weekend_data.weekend.timing_run_id
        if weekend_data and weekend_data.weekend
        else None,
    )
