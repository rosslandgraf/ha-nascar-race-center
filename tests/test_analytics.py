"""Handmade numerical examples, independent expected arithmetic, no NASCAR I/O."""

import json
import math
from dataclasses import FrozenInstanceError, asdict, replace

import pytest
from test_history import KEY, fixture

from custom_components.nascar_race_center.analytics import analyze_history
from custom_components.nascar_race_center.analytics_models import (
    WINDOW_CHOICES,
    AnalyticsQuery,
    AnalyticsStatus,
)
from custom_components.nascar_race_center.history_models import (
    DriverLaps,
    HistoricalData,
    HistoricalDriver,
    HistoricalLap,
    HistoryProvenance,
    HistoryResponse,
    HistoryResult,
    ReportedMetric,
)
from custom_components.nascar_race_center.history_models import (
    HistoryDataset as Kind,
)
from custom_components.nascar_race_center.history_models import (
    HistoryStatus as Status,
)
from custom_components.nascar_race_center.history_parser import PARSERS


def source(driver_id=101, values=(10, 12, 14, 16, 18), positions=None, numbers=None):
    positions = positions if positions is not None else [2] * len(values)
    numbers = numbers if numbers is not None else range(1, len(values) + 1)
    return DriverLaps(
        HistoricalDriver(driver_id, "07", "Same display name"),
        None,
        tuple(
            HistoricalLap(n, v, None, p)
            for n, v, p in zip(numbers, values, positions, strict=True)
        ),
    )


def result(kind, data=None, status=Status.AVAILABLE, key=KEY):
    return HistoryResult(
        status,
        HistoryProvenance(
            kind, key, "path_context_only", "unverified_context", "synthetic"
        ),
        data,
    )


def response(*drivers):
    return HistoryResponse(
        KEY, (result(Kind.LAPS, HistoricalData(laps=tuple(drivers))),)
    )


def query(ids=(101,), **kwargs):
    return AnalyticsQuery(
        KEY,
        ids,
        first_lap=kwargs.pop("first_lap", 1),
        last_lap=kwargs.pop("last_lap", 5),
        **kwargs,
    )


def metric_values(row):
    return {m.name: m.value for m in row.metrics}


def fixture_result(kind):
    return result(kind, PARSERS[kind](fixture(kind), KEY))


def test_known_exact_numerical_example_and_defined_consistency():
    observations = response(source())
    output = analyze_history(observations, query())
    row = output.drivers[0]
    values = metric_values(row)
    assert values["mean"] == 14
    assert values["median"] == 14
    assert values["minimum"] == values["fastest_reported_lap"] == 10
    assert values["maximum"] == 18
    assert values["range"] == 8
    # Deviations -4,-2,0,2,4: squared sum 40; population variance 8.
    assert values["population_stddev"] == pytest.approx(math.sqrt(8))
    assert values["coefficient_of_variation"] == pytest.approx(math.sqrt(8) / 14)
    assert values["mean_absolute_consecutive_change"] == 2
    assert values["consecutive_pair_count"] == 4
    assert row.fastest_lap == 1
    assert row.coverage.valid_times == row.coverage.basis_samples == 5
    assert row.coverage.invalid_times == row.coverage.missing_laps == 0
    assert all("seconds" not in m.unit for m in row.metrics)
    assert output.status == AnalyticsStatus.AVAILABLE
    assert output == analyze_history(observations, query())
    with pytest.raises(FrozenInstanceError):
        row.fastest_lap = 10


@pytest.mark.parametrize("size", WINDOW_CHOICES)
def test_consecutive_windows_have_exact_bounds_and_arithmetic(size):
    row = analyze_history(
        response(source(values=tuple(range(1, size + 3)))),
        query(last_lap=size + 2, windows=(size,)),
    ).drivers[0]
    windows = row.rolling[0].windows
    assert len(windows) == 3
    assert [(w.first_lap, w.last_lap) for w in windows] == [
        (1, size),
        (2, size + 1),
        (3, size + 2),
    ]
    assert windows[0].mean == windows[0].median == (size + 1) / 2
    assert windows[-1].minimum == 3
    assert windows[-1].maximum == size + 2
    assert row.rolling[0].best_mean.value == (size + 1) / 2


@pytest.mark.parametrize(
    "invalid", [None, 0, -1, float("nan"), float("inf"), -float("inf"), True, False]
)
def test_invalid_or_missing_time_never_bridges_window(invalid):
    row = analyze_history(
        response(source(values=(10, 12, invalid, 16, 18, 20))), query(last_lap=6)
    ).drivers[0]
    assert row.coverage.valid_times == 5
    assert row.coverage.missing_times == (1 if invalid is None else 0)
    assert row.coverage.invalid_times == (0 if invalid is None else 1)
    assert not row.rolling[0].windows
    assert [(r.first_lap, r.last_lap) for r in row.consecutive_runs] == [(1, 2), (4, 6)]
    assert row.samples[3].consecutive_time_delta is None
    assert metric_values(row)["mean"] == pytest.approx(15.2)
    assert row.status == AnalyticsStatus.PARTIAL
    json.dumps(asdict(row), allow_nan=False)


def test_missing_numbered_lap_breaks_windows_and_counts_absence():
    row = analyze_history(
        response(source(values=(10, 12, None, 18), numbers=(1, 2, 4, 5))),
        query(last_lap=7),
    ).drivers[0]
    assert [(g.first_lap, g.last_lap) for g in row.gaps] == [(3, 3), (6, 7)]
    assert row.coverage.recorded_laps == 4
    assert row.coverage.missing_laps == 3
    assert row.coverage.missing_times == 1
    assert not row.rolling[0].windows
    assert row.positions.gaps[0].first_lap == 3


@pytest.mark.parametrize("values", [(), (None,), (0,), (-1,)])
def test_zero_valid_laps_are_explicitly_unavailable(values):
    row = analyze_history(response(source(values=values)), query()).drivers[0]
    assert row.coverage.valid_times == 0
    assert row.fastest_lap is None
    assert all(
        m.value is None and m.reason
        for m in row.metrics
        if m.name != "consecutive_pair_count"
    )
    assert not row.consecutive_runs and not row.rolling[0].windows


@pytest.mark.parametrize(
    "values,expected", [((3,), 3), ((2, 4), 3), ((2, 4, 6, 8), 5), ((999,), 999)]
)
def test_small_even_samples_and_positive_999_are_not_guessed_sentinels(
    values, expected
):
    row = analyze_history(response(source(values=values)), query()).drivers[0]
    assert metric_values(row)["median"] == expected
    if len(values) == 1:
        assert row.metrics[6].reason == "requires_two_valid_laps"
    assert row.coverage.valid_times == len(values)


def test_original_order_and_lap_indexed_position_progression():
    row = analyze_history(
        response(
            source(
                values=(14, 10, 12, 18), numbers=(3, 1, 2, 5), positions=(1, 8, 6, 3)
            )
        ),
        query(),
    ).drivers[0]
    assert [s.lap for s in row.samples] == [3, 1, 2, 5]
    assert [s.source_index for s in row.samples] == [0, 1, 2, 3]
    positions = row.positions
    assert [(p.lap, p.position) for p in positions.points] == [
        (1, 8),
        (2, 6),
        (3, 1),
        (5, 3),
    ]
    assert positions.start.lap == 1 and positions.end.lap == 5
    assert positions.change.value == 5
    assert positions.best.value == 1 and positions.worst.value == 8
    assert positions.first_position_samples.value == 1
    assert [(g.first_lap, g.last_lap) for g in positions.gaps] == [(4, 4)]


@pytest.mark.parametrize("invalid", [None, 0, -1, 999, True])
def test_sparse_position_observations_do_not_invent_positions(invalid):
    row = analyze_history(
        response(source(values=(10, 12, 14), positions=(invalid, 3, invalid))),
        query(last_lap=3),
    ).drivers[0]
    assert len(row.positions.points) == 1
    assert row.positions.change.value is None
    assert row.positions.first_position_samples.value == 0
    assert row.coverage.usable_positions == 1


@pytest.mark.parametrize(
    "basis,left_mean,right_mean,difference",
    [("all_available", 20, 50, -30), ("overlapping_valid_laps", 25, 50, -25)],
)
def test_comparison_uses_explicit_basis(basis, left_mean, right_mean, difference):
    output = analyze_history(
        response(
            source(values=(10, 20, 30), numbers=(1, 2, 4)),
            source(202, (40, 50, 60), numbers=(2, 3, 4)),
        ),
        query((101, 202), time_basis=basis),
    )
    comp = next(m for m in output.comparisons[0].metrics if m.name == "mean")
    assert comp.left_value == left_mean
    assert comp.right_value == right_mean
    assert comp.difference.value == difference
    assert comp.relative_percent.value == difference / right_mean * 100
    assert output.drivers[0].coverage.basis_samples == (
        2 if basis == "overlapping_valid_laps" else 3
    )
    assert len(output.drivers[0].positions.points) == 3


def test_unequal_counts_missing_driver_and_zero_relative_reference():
    output = analyze_history(
        response(source(), source(202, (10, 10))), query((101, 202, 303))
    )
    assert len(output.comparisons) == 3
    assert output.drivers[2].reason == "driver_not_recorded"
    comp = next(
        m for m in output.comparisons[0].metrics if m.name == "population_stddev"
    )
    assert comp.difference.available
    assert comp.relative_percent.reason == "zero_reference_value"
    common = analyze_history(
        response(source()), query((101, 202), time_basis="overlapping_valid_laps")
    )
    assert all(d.coverage.basis_samples == 0 for d in common.drivers)


def test_tied_fastest_lap_uses_lowest_lap_and_selected_range():
    row = analyze_history(
        response(source(values=(10, 9, 9, 1), numbers=(10, 8, 9, 7))),
        query(first_lap=8, last_lap=10),
    ).drivers[0]
    assert row.fastest_lap == 8
    assert row.coverage.out_of_range == 1
    assert metric_values(row)["minimum"] == 9


@pytest.mark.parametrize(
    "change", ["driver", "lap", "lap_bool", "driver_bool", "invalid_lap"]
)
def test_conflicting_and_duplicate_identities_fail_selected_feed(change):
    driver = source()
    drivers = (driver,)
    if change == "driver":
        drivers += (driver,)
    elif change == "lap":
        drivers = (replace(driver, laps=driver.laps + (driver.laps[0],)),)
    elif change == "driver_bool":
        drivers = (replace(driver, driver=HistoricalDriver(True)),)
    else:
        drivers = (
            replace(
                driver,
                laps=(
                    replace(driver.laps[0], lap=True if change == "lap_bool" else -1),
                ),
            ),
        )
    output = analyze_history(response(*drivers), query())
    assert output.status == AnalyticsStatus.INVALID
    assert output.evidence[0].status == Status.INVALID
    assert not output.drivers[0].samples


@pytest.mark.parametrize(
    "field,value", [("season", 2025), ("series_id", 2), ("race_id", 88002)]
)
def test_provenance_or_response_context_mismatch_is_not_joined(field, value):
    other = replace(KEY, **{field: value})
    original = response(source())
    for bad in (
        replace(original, key=other),
        replace(
            original,
            results=(
                replace(
                    original.results[0],
                    provenance=replace(original.results[0].provenance, requested=other),
                ),
            ),
        ),
    ):
        output = analyze_history(bad, query())
        assert output.status == AnalyticsStatus.INVALID
        assert output.evidence[0].reason == "race_identity"


def test_weekend_results_stages_reported_fields_and_conflicting_context():
    output = analyze_history(
        HistoryResponse(
            KEY,
            tuple(
                fixture_result(k)
                for k in (Kind.WEEKEND, Kind.STAGES, Kind.LOOP, Kind.AVERAGES)
            ),
        ),
        query((99002, 101)),
    )
    row = output.performance[0]
    assert row.result.finishing_position == 1
    assert row.result.starting_position == 2
    assert row.result.laps_completed == 5 and row.result.laps_led == 3
    assert row.result.points_earned == 40 and row.result.playoff_points_earned == 0
    assert row.start_finish_position_change.value == 1
    assert row.start_finish_position_change.classification == "derived"
    assert row.reported_position_difference.value is None
    assert row.reported_position_difference.classification == "recorded"
    assert [(s.dataset, s.points) for s in row.stages] == [
        (Kind.WEEKEND, 10),
        (Kind.STAGES, 0),
    ]
    assert all(s.conflict for s in row.stages)
    assert row.stages[0].run_namespace is None
    assert row.stages[1].run_namespace == "stage_run"
    assert output.status == AnalyticsStatus.PARTIAL
    assert output.performance[1].result_reason == "driver_not_in_reported_results"
    assert output.race_metrics[0].value == 5


def test_loop_and_average_labels_sentinels_and_formulas_stay_reported():
    output = analyze_history(
        HistoryResponse(
            KEY, (fixture_result(Kind.LOOP), fixture_result(Kind.AVERAGES))
        ),
        query((99002,)),
    )
    groups = output.performance[0].reported_metrics
    loop = {m.field: m for m in groups[0].metrics}
    assert loop["rating"].value == 99.5
    assert loop["closing_laps_diff"].value == -1
    averages = {m.field: m for m in groups[1].metrics}
    assert groups[1].title == "Fictional Practice Label"
    assert averages["Con10Lap"].value == 999
    assert averages["Con10Lap"].interpretation == "candidate_sentinel"
    assert averages["Con10LapRank"].value is None
    assert all(g.classification == "recorded" for g in groups)
    assert all(m.value is None for m in output.drivers[0].metrics[:-1])


@pytest.mark.parametrize(
    "field,value",
    [
        ("race_id", 9),
        ("series_id", 2),
        ("season", 2025),
        ("run_namespace", "timing_run"),
        ("run_id", None),
    ],
)
def test_archived_stage_context_is_independently_validated(field, value):
    stage_result = fixture_result(Kind.STAGES)
    stage = stage_result.data.stages[0]
    bad = replace(
        stage_result,
        data=replace(
            stage_result.data,
            stages=(replace(stage, context=replace(stage.context, **{field: value})),),
        ),
    )
    output = analyze_history(
        HistoryResponse(KEY, (fixture_result(Kind.WEEKEND), bad)), query((99002,))
    )
    assert output.evidence[1].status == Status.INVALID
    assert output.performance[0].result is not None
    assert len(output.performance[0].stages) == 1


def test_dnf_missing_results_and_sentinel_positions_are_preserved_without_inference():
    weekend_result = fixture_result(Kind.WEEKEND)
    weekend = weekend_result.data.weekend
    retired = replace(
        weekend.results[0],
        finishing_status="Synthetic DNF",
        finishing_position=999,
        laps_completed=2,
    )
    output = analyze_history(
        HistoryResponse(
            KEY,
            (
                replace(
                    weekend_result,
                    data=replace(
                        weekend_result.data,
                        weekend=replace(weekend, results=(retired,)),
                    ),
                ),
            ),
        ),
        query((99002,)),
    )
    assert output.performance[0].result.finishing_status == "Synthetic DNF"
    assert output.performance[0].result.laps_completed == 2
    assert output.performance[0].start_finish_position_change.value is None
    for rows in (None, ()):
        missing = replace(
            weekend_result,
            data=replace(weekend_result.data, weekend=replace(weekend, results=rows)),
        )
        output = analyze_history(HistoryResponse(KEY, (missing,)), query((99002,)))
        assert output.performance[0].result is None


@pytest.mark.parametrize("status", list(Status))
def test_mixed_available_empty_unsupported_and_failed_datasets(status):
    peer = result(
        Kind.LOOP,
        HistoricalData() if status in (Status.AVAILABLE, Status.EMPTY) else None,
        status,
    )
    output = analyze_history(
        HistoryResponse(KEY, (*response(source()).results, peer)), query()
    )
    assert metric_values(output.drivers[0])["mean"] == 14
    assert output.evidence[1].status == status
    assert output.status == (
        AnalyticsStatus.AVAILABLE
        if status in (Status.AVAILABLE, Status.EMPTY)
        else AnalyticsStatus.PARTIAL
    )


def test_pits_are_not_attached_by_name_number_or_row_order():
    output = analyze_history(
        HistoryResponse(KEY, (fixture_result(Kind.PITS), fixture_result(Kind.WEEKEND))),
        query((99002,)),
    )
    assert output.performance[0].result is not None
    assert not hasattr(output.performance[0], "pits")
    assert output.evidence[0].dataset == Kind.PITS


@pytest.mark.parametrize(
    "kwargs",
    [
        {"driver_ids": ()},
        {"driver_ids": tuple(range(1, 10))},
        {"driver_ids": (1, 1)},
        {"driver_ids": (True,)},
        {"driver_ids": (0,)},
        {"driver_ids": ("101",)},
        {"first_lap": -1},
        {"last_lap": True},
        {"first_lap": 5, "last_lap": 4},
        {"first_lap": 0, "last_lap": 5000},
        {"windows": (3,)},
        {"windows": (5, 5)},
        {"windows": (True,)},
        {"time_basis": "green_flag"},
        {"driver_ids": tuple(range(1, 9)), "last_lap": 5000, "windows": WINDOW_CHOICES},
    ],
)
def test_request_resource_and_selection_bounds(kwargs):
    defaults = dict(driver_ids=(101,), first_lap=1, last_lap=5)
    defaults.update(kwargs)
    with pytest.raises(ValueError):
        AnalyticsQuery(KEY, **defaults)


def test_large_accepted_dataset_and_bounded_rolling_work():
    drivers = tuple(
        source(n, tuple(float(i % 10 + 10) for i in range(5000))) for n in range(1, 11)
    )
    output = analyze_history(
        response(*drivers), query(tuple(range(1, 9)), last_lap=5000)
    )
    assert len(output.drivers) == 8
    assert len(output.comparisons) == 28
    assert sum(len(d.samples) for d in output.drivers) == 40000
    assert sum(len(d.rolling[0].windows) for d in output.drivers) == 39968
    too_many = replace(
        drivers[0], laps=drivers[0].laps + (HistoricalLap(5001, 10, None, 2),)
    )
    assert (
        analyze_history(response(too_many), query()).status == AnalyticsStatus.INVALID
    )
    assert (
        analyze_history(response(*drivers, source(11, (10,))), query()).status
        == AnalyticsStatus.INVALID
    )


def test_unsupported_loop_fields_are_not_interpreted():
    reported = fixture_result(Kind.LOOP)
    loop = reported.data.loops[0]
    driver = replace(
        loop.drivers[0], metrics=(ReportedMetric("invented_tire_age", 10),)
    )
    bad = replace(
        reported, data=replace(reported.data, loops=(replace(loop, drivers=(driver,)),))
    )
    assert (
        analyze_history(HistoryResponse(KEY, (bad,)), query((99002,)))
        .evidence[0]
        .reason
        == "unsupported_metric"
    )


@pytest.mark.parametrize(
    "values,expected_sd",
    [((1e12 - 1, 1e12), 0.5), ((5e-324, 5e-324), 0), ((1e308, 1e308), 0)],
)
def test_numerical_stability_for_close_large_tiny_and_extreme_samples(
    values, expected_sd
):
    row = analyze_history(
        response(source(values=values)), query(last_lap=2, windows=())
    ).drivers[0]
    values_out = metric_values(row)
    assert values_out["population_stddev"] == expected_sd
    assert values_out["mean"] > 0
    assert math.isfinite(values_out["median"])
    json.dumps(asdict(row), allow_nan=False)


def test_missing_times_and_missing_positions_are_distinct():
    row = analyze_history(
        response(source(values=(10, 12), positions=(None, None))), query(last_lap=2)
    ).drivers[0]
    assert row.coverage.valid_times == 2
    assert row.coverage.usable_positions == 0
    assert row.positions.start is row.positions.end is None
    assert row.positions.first_position_samples.value is None
    assert row.positions.first_position_samples.reason == "no_usable_positions"


def test_stage_run_and_driver_duplicates_are_not_arbitrarily_selected():
    reported = fixture_result(Kind.STAGES)
    stage = reported.data.stages[0]
    for rows in (
        (stage, stage),
        (stage, replace(stage, number=2, context=replace(stage.context, run_id=11))),
        (replace(stage, results=stage.results + stage.results),),
    ):
        bad = replace(reported, data=replace(reported.data, stages=rows))
        assert (
            analyze_history(HistoryResponse(KEY, (bad,)), query((99002,))).status
            == AnalyticsStatus.INVALID
        )


@pytest.mark.parametrize("kind", [Kind.WEEKEND, Kind.LOOP, Kind.AVERAGES])
def test_duplicate_reported_driver_ids_fail_their_own_dataset(kind):
    reported = fixture_result(kind)
    data = reported.data
    if kind == Kind.WEEKEND:
        data = replace(
            data, weekend=replace(data.weekend, results=data.weekend.results * 2)
        )
    elif kind == Kind.LOOP:
        data = replace(
            data, loops=(replace(data.loops[0], drivers=data.loops[0].drivers * 2),)
        )
    else:
        data = replace(
            data,
            averages=(replace(data.averages[0], drivers=data.averages[0].drivers * 2),),
        )
    output = analyze_history(
        HistoryResponse(
            KEY, (*response(source()).results, replace(reported, data=data))
        ),
        query(),
    )
    assert output.status == AnalyticsStatus.PARTIAL
    assert output.evidence[1].reason == "driver_identity"
    assert metric_values(output.drivers[0])["mean"] == 14


def test_weekend_identity_results_runs_and_namespace_preservation():
    reported = fixture_result(Kind.WEEKEND)
    weekend = reported.data.weekend
    output = analyze_history(HistoryResponse(KEY, (reported,)), query((99002,)))
    assert output.race_timing_run_id == 10
    session = output.performance[0].sessions[0]
    assert session.weekend_run_id == 77001
    assert session.timing_run_id == 6
    assert session.result.results_run_id == 77001
    assert output.performance[0].result.results_run_id is None
    wrong = replace(
        reported,
        data=replace(
            reported.data, weekend=replace(weekend, key=replace(KEY, season=2025))
        ),
    )
    assert (
        analyze_history(HistoryResponse(KEY, (wrong,)), query((99002,)))
        .evidence[0]
        .reason
        == "race_identity"
    )
    first = replace(weekend.results[0], results_run_id=7)
    second = replace(first, driver=HistoricalDriver(99003), results_run_id=8)
    wrong = replace(
        reported,
        data=replace(reported.data, weekend=replace(weekend, results=(first, second))),
    )
    assert (
        analyze_history(HistoryResponse(KEY, (wrong,)), query((99002,)))
        .evidence[0]
        .reason
        == "conflicting_results_run"
    )


def test_duplicate_dataset_and_unvalidated_provenance_are_unavailable():
    original = response(source())
    duplicate = replace(original, results=original.results * 2)
    output = analyze_history(duplicate, query())
    assert all(e.reason == "duplicate_dataset" for e in output.evidence)
    unvalidated = replace(
        original.results[0],
        provenance=replace(original.results[0].provenance, validation="not_validated"),
    )
    assert (
        analyze_history(HistoryResponse(KEY, (unvalidated,)), query())
        .evidence[0]
        .reason
        == "unvalidated_source"
    )


def test_same_name_and_car_do_not_substitute_for_nascar_driver_identity():
    output = analyze_history(
        response(source(), source(202, (30, 30, 30, 30, 30))), query((101, 202))
    )
    assert metric_values(output.drivers[0])["mean"] == 14
    assert metric_values(output.drivers[1])["mean"] == 30


@pytest.mark.parametrize(
    "key",
    [replace(KEY, season=2019), replace(KEY, series_id=2), replace(KEY, series_id=3)],
)
def test_explicit_race_keys_do_not_collide_across_years_or_series(key):
    original = response(source())
    adjusted = replace(
        original,
        key=key,
        results=(
            replace(
                original.results[0],
                provenance=replace(original.results[0].provenance, requested=key),
            ),
        ),
    )
    output = analyze_history(adjusted, replace(query(), key=key))
    assert output.query.key == key
    assert metric_values(output.drivers[0])["mean"] == 14


def test_common_lap_windows_require_valid_recordings_for_every_selected_driver():
    left = source(values=tuple(range(10, 21)))
    right = source(
        202, tuple(range(20, 31)), numbers=(1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12)
    )
    output = analyze_history(
        response(left, right),
        query((101, 202), last_lap=12, time_basis="overlapping_valid_laps"),
    )
    for driver in output.drivers:
        assert [(w.first_lap, w.last_lap) for w in driver.rolling[0].windows] == [
            (1, 5),
            (7, 11),
        ]
    best = next(m for m in output.comparisons[0].metrics if m.name == "best_5_lap_mean")
    assert best.left_value == 12
    assert best.right_value == 22


@pytest.mark.parametrize("kind", [Kind.WEEKEND, Kind.LOOP, Kind.AVERAGES, Kind.STAGES])
def test_all_empty_or_missing_data_has_explicit_availability(kind):
    for data, status in ((HistoricalData(), Status.EMPTY), (None, Status.UNVERIFIED)):
        output = analyze_history(
            HistoryResponse(KEY, (result(kind, data, status),)), query()
        )
        assert output.status == AnalyticsStatus.UNAVAILABLE
        assert output.reason == "no_usable_analytics_observations"
        assert not any(m.available for m in output.race_metrics)
