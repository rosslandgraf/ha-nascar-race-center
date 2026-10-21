"""Observed shapes with fictional values; race association never uses guesses."""

import json
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from test_live_timing import timing_payload

from custom_components.nascar_race_center.models import parse_live
from custom_components.nascar_race_center.scoring import (
    Provenance,
    RaceContext,
    association_state,
    latest_pit,
    parse_embedded_pits,
    parse_pit_feed,
    parse_points_feed,
    parse_stage_feed,
)

ROOT = Path(__file__).parent / "fixtures" / "phase3b"
NOW = datetime(2026, 10, 20, 20, tzinfo=UTC)
ACTIVE = RaceContext(1, 99001, 7, "live_timing")


def fixture(name):
    return json.loads((ROOT / f"{name}.json").read_text())


def embedded_payload():
    payload = timing_payload()
    extra = fixture("embedded")
    payload["stage"] = extra["stage"]
    payload["vehicles"][0]["pit_stops"] = extra["pit_stops"]
    return payload


def trusted_feed(kind, *, clock=NOW, context=ACTIVE):
    """Synthetic provider contract, NEVER a CF adapter association heuristic."""
    parser = {"stages": parse_stage_feed, "points": parse_points_feed}[kind]
    feed = parser(fixture(kind), Provenance("synthetic", "synthetic", clock))
    return replace(
        feed,
        contexts=(context,),
        stages=tuple(replace(stage, context=context) for stage in feed.stages),
        points=tuple(replace(row, context=context) for row in feed.points),
    )


def test_embedded_pit_identity_raw_timing_and_stage_descriptor():
    snapshot = parse_live(embedded_payload())
    driver = snapshot.leaderboard.by_driver[99002]
    assert driver.pit_stops[0].entry_time == 650.5
    assert driver.pit_stops[0].exit_time == 680.2
    assert driver.pit_stops[0].position_change == 3
    assert driver.pit_stops[1].exit_time is None
    assert driver.pit_stops[1].exit_position is None
    assert latest_pit(driver.pit_stops).lap == 40
    assert snapshot.stage.number == 2
    assert snapshot.stage.finish_at_lap == 80
    assert snapshot.stage.laps_in_stage == 40
    with pytest.raises(FrozenInstanceError):
        snapshot.stage.number = 3
    assert not hasattr(driver, "pit_count")  # array length isn't completed stops
    assert not hasattr(snapshot.stage, "completed")


@pytest.mark.parametrize("value", [None, {}, "unknown", [None], [{}] * 1001])
def test_pit_schema_failure_does_not_discard_position_or_stage(value):
    payload = embedded_payload()
    payload["vehicles"][0]["pit_stops"] = value
    snapshot = parse_live(payload)
    driver = snapshot.leaderboard.by_driver[99002]
    assert driver.pits_failed and driver.pit_stops is None
    assert driver.position == 2
    assert snapshot.stage.number == 2
    assert snapshot.flag == "green"


@pytest.mark.parametrize("value", [None, [], "bad", 2])
def test_stage_schema_failure_does_not_discard_pits_or_flag(value):
    payload = embedded_payload()
    payload["stage"] = value
    snapshot = parse_live(payload)
    assert snapshot.stage_failed and snapshot.stage is None
    assert latest_pit(snapshot.leaderboard.by_driver[99002].pit_stops).lap == 40
    assert snapshot.flag == "green"


@pytest.mark.parametrize("value", [None, -1, 0, True, "NaN", "inf", {}, float("nan")])
def test_nonphysical_pit_clocks_are_unknown(value):
    payload = fixture("embedded")["pit_stops"]
    payload[0].update(pit_in_elapsed_time=value, pit_out_elapsed_time=value)
    stop = parse_embedded_pits(payload)[0]
    assert stop.entry_time is None and stop.exit_time is None
    assert stop.position_change == 3


def test_duplicate_and_ambiguous_same_lap_records_never_select_list_order():
    rows = fixture("embedded")["pit_stops"]
    duplicate = [rows[0], rows[0]]
    assert latest_pit(parse_embedded_pits(duplicate)).lap == 20
    duplicate[1] = {**rows[0], "pit_in_rank": 9}
    assert latest_pit(parse_embedded_pits(duplicate)) is None
    assert (
        latest_pit(parse_embedded_pits([{**rows[0], "pit_in_lap_count": None}])) is None
    )
    assert latest_pit(()) is None


def test_standalone_pits_preserve_activity_but_never_join_car_or_name():
    feed = parse_pit_feed(fixture("pits"), Provenance("pits"))
    row = feed.pits[0]
    assert row.car_number == "07"
    assert row.stop.position_change == -2
    assert row.stop_duration is None and row.box_stop_time is None
    assert row.total_duration == 29.7
    assert row.tires_changed == (True, False, True, False)
    assert row.stop_type == "reported synthetic type"
    assert feed.contexts == ()
    assert association_state(feed, ACTIVE, NOW) == "context_unknown"
    assert not hasattr(row, "driver_id")


def test_results_and_points_are_reported_without_formula_or_official_finality():
    stages = parse_stage_feed(fixture("stages"), Provenance("stages"))
    assert stages.stages[1].driver(99002).points == 0
    assert stages.stages[0].driver(99002).position == 2
    assert stages.contexts == (RaceContext(None, 99005, 4, "stage_run"),)
    assert association_state(stages, ACTIVE, NOW) == "context_mismatch"
    points = parse_points_feed(fixture("points"), Provenance("points"))
    row = points.driver_points(99002)
    assert row.membership_id == 123456 and row.driver_id == 99002
    assert points.driver_points(123456) is None
    assert row.points == 2040 and row.race_points == 31
    assert row.bonus_points is None
    assert row.stage_points == (9, 0, None)
    assert row.stage_winner == (False, False, None)
    assert row.delta_leader == -12 and row.delta_next == -2
    assert row.wins == 2 and row.top_five == 4
    assert row.fastest_lap_point is False
    assert points.classification == stages.classification == "provisional"
    assert points.contexts[0].race_id is None
    assert association_state(points, ACTIVE, NOW) == "context_unknown"


@pytest.mark.parametrize("value", [None, 0, -1, True, "", "NaN", "-1"])
def test_invalid_context_never_becomes_active_race(value):
    rows = fixture("points")
    rows[0].update(series_id=value, race_id=value, run_id=value)
    feed = parse_points_feed(rows, Provenance("points", source_updated_at=NOW))
    assert feed.contexts[0].race_id is None
    assert association_state(feed, ACTIVE, NOW) == "context_unknown"


@pytest.mark.parametrize(
    "context,expected",
    [
        (RaceContext(2, 99001, 7, "live_timing"), "context_mismatch"),
        (RaceContext(1, 99002, 7, "live_timing"), "context_mismatch"),
        (RaceContext(1, 99001, 8, "live_timing"), "context_mismatch"),
        (RaceContext(1, 99001, 7, "weekend_run"), "namespace_unverified"),
        (RaceContext(1, 99001, 7, "stage_run"), "namespace_unverified"),
        (RaceContext(1, 99001, 7, "points_run"), "namespace_unverified"),
        (RaceContext(1, 99001, 7), "namespace_unverified"),
        (RaceContext(None, 99001, 7, "live_timing"), "context_unknown"),
        (RaceContext(1, None, 7, "live_timing"), "context_unknown"),
        (RaceContext(1, 99001, None, "live_timing"), "context_unknown"),
        (RaceContext(1, 99001, 0, "live_timing"), "context_unknown"),
        (RaceContext(1, 99001, -1, "live_timing"), "context_unknown"),
        (RaceContext(1, 99001, True, "live_timing"), "context_unknown"),
    ],
)
def test_context_requires_positive_matching_ids_and_verified_namespace(
    context, expected
):
    assert (
        association_state(trusted_feed("points", context=context), ACTIVE, NOW)
        == expected
    )


@pytest.mark.parametrize(
    "clock,expected",
    [
        (None, "freshness_unknown"),
        (NOW.replace(tzinfo=None), "freshness_unknown"),
        (NOW + timedelta(hours=1), "freshness_unknown"),
        (NOW - timedelta(minutes=16), "stale"),
        (NOW, "available"),
    ],
)
def test_content_clock_not_http_or_peer_feed_proves_freshness(clock, expected):
    feed = trusted_feed("points", clock=clock)
    assert association_state(feed, ACTIVE, NOW) == expected
    # A 304/cache/HTTP refresh changes transport context, not content age.
    refreshed = replace(feed, provenance=replace(feed.provenance, retrieved_at=NOW))
    assert association_state(refreshed, ACTIVE, NOW) == expected


def test_mixed_races_and_archived_scope_cannot_supply_live_scoring():
    feed = trusted_feed("points")
    mixed = replace(feed, contexts=(ACTIVE, replace(ACTIVE, race_id=99999)))
    assert association_state(mixed, ACTIVE, NOW) == "conflicting_context"
    archived = replace(feed, provenance=replace(feed.provenance, scope="historical"))
    assert association_state(archived, ACTIVE, NOW) == "historical"
    assert association_state(feed, replace(ACTIVE, season=2026), NOW) == "available"
    previous_year = replace(feed, contexts=(replace(ACTIVE, season=2025),))
    assert (
        association_state(previous_year, replace(ACTIVE, season=2026), NOW)
        == "context_mismatch"
    )


@pytest.mark.parametrize(
    "parser,name", [(parse_stage_feed, "stages"), (parse_points_feed, "points")]
)
def test_ambiguous_driver_id_fails_optional_dataset(parser, name):
    rows = fixture(name)
    if name == "stages":
        rows[0]["results"].append(rows[0]["results"][0])
    else:
        rows.append(rows[0])
    with pytest.raises(ValueError):
        parser(rows, Provenance(name))


@pytest.mark.parametrize(
    "parser,limit",
    [(parse_pit_feed, 10000), (parse_stage_feed, 20), (parse_points_feed, 200)],
)
@pytest.mark.parametrize("payload", [None, {}, [None], "bad"])
def test_schema_drift_is_explicit(parser, limit, payload):
    with pytest.raises(ValueError):
        parser(payload, Provenance("synthetic"))
    with pytest.raises(ValueError):
        parser([{}] * (limit + 1), Provenance("synthetic"))


def test_numeric_strings_nulls_sentinels_and_zero_scores_are_field_specific():
    rows = fixture("points")
    rows[0].update(
        points=None,
        points_position=0,
        points_earned_this_race=-1,
        bonus_points=True,
        stage_1_points="0",
        stage_1_winner="false",
    )
    result = parse_points_feed(rows, Provenance("points")).points[0]
    assert result.points is None and result.position is None
    assert result.race_points is None and result.bonus_points is None
    assert result.stage_points[0] == 0 and result.stage_winner[0] is None
    rows[0].pop("driver_id")
    with pytest.raises(ValueError):
        parse_points_feed(rows, Provenance("points"))  # no membership-ID fallback


def test_imported_structures_ground_fixture_keys_without_using_redacted_values():
    root = Path(__file__).parents[1] / "docs" / "nascar-api-reference"
    for name, folder, original in (
        ("pits", "04_Pit_Stops_and_Stages", "03_live-pit-data"),
        ("stages", "04_Pit_Stops_and_Stages", "05_live-stage-points"),
        ("points", "05_Points_and_Standings", "04_live-points"),
    ):
        structure = json.loads(
            (root / folder / f"{original}.structural.json").read_text()
        )
        assert set(fixture(name)[0]) <= set(structure[0])
    structure = json.loads(
        (root / "01_Live_Race_Data/01_live-feed.structural.json").read_text()
    )
    assert set(fixture("embedded")["stage"]) <= set(structure["stage"])
    assert set(fixture("embedded")["pit_stops"][0]) <= set(
        structure["vehicles"][0]["pit_stops"][0]
    )
