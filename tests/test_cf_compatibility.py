"""Observed structures with invented values; no NASCAR network or raw captures."""

import copy
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from test_api import Response, client_with

from custom_components.nascar_race_center.endpoints import (
    LIVE_FEED,
)
from custom_components.nascar_race_center.models import (
    SchemaError,
    merge_schedule,
    parse_live,
    parse_schedule,
    parse_schedule_feed,
)
from custom_components.nascar_race_center.provider import CFProvider
from custom_components.nascar_race_center.reference import parse_drivers, parse_tracks

FIXTURES = Path(__file__).parent / "fixtures" / "phase3da"


def fixture(name):
    return json.loads((FIXTURES / f"{name}.json").read_text())


@pytest.mark.parametrize(
    ("name", "endpoint"),
    [
        ("live", "01"),
        ("schedule", "06"),
        ("sessions", "09"),
        ("drivers", "07"),
        ("tracks", "08"),
    ],
)
def test_fixture_paths_and_types_have_observed_evidence(name, endpoint):
    """Prevent fictional values from introducing unsupported production fields."""
    profiles = json.loads(
        (
            Path(__file__).parents[1]
            / "docs/nascar-api-reference/Documentation/field_profiles.json"
        ).read_text()
    )[endpoint]

    def check(value, path="$"):
        kind = {
            dict: "object",
            list: "array",
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            type(None): "null",
        }[type(value)]
        assert kind in profiles[path]["types"], path
        if isinstance(value, dict):
            for key, child in value.items():
                check(child, f"{path}.{key}")
        elif isinstance(value, list):
            for child in value:
                check(child, f"{path}[]")

    check(fixture(name))


def test_observed_live_identity_embedded_pits_stage_and_precision():
    snapshot = parse_live(fixture("live"))
    assert snapshot.session_key == (1, 99051, 17)
    assert snapshot.source_updated_at == datetime(
        2026, 10, 21, 12, 4, 25, 123456, tzinfo=UTC
    )
    driver = snapshot.leaderboard.by_driver[99011]
    assert driver.car_number == "07"
    assert driver.running_status is None  # status 3 has no invented meaning
    assert driver.status_code == 3
    assert driver.is_on_track is False
    assert driver.gap == 0
    assert driver.pit_stops[0].position_change == -2
    assert driver.pit_stops[0].exit_time is None
    assert driver.pit_stops[0].exit_position is None
    assert snapshot.stage.number == 2
    assert snapshot.stage.finish_at_lap == 60
    reference = {
        driver.driver_id: driver for driver in parse_drivers(fixture("drivers"))
    }
    assert reference[driver.driver_id].name == driver.name
    assert 88011 not in reference  # Driver_ID is a separate namespace


@pytest.mark.parametrize(
    "value", [None, "", "2026-10-21T12:04:25.1234567", 123456789, "bad"]
)
def test_no_numeric_or_naive_clock_fallback(value):
    payload = fixture("live")
    payload["time_of_day_os"] = value
    assert parse_live(payload).source_updated_at is None


def test_unknown_codes_survive_without_new_status_meanings():
    payload = fixture("live")
    payload.update(flag_state=777, run_type=888)
    snapshot = parse_live(payload)
    assert snapshot.flag is None
    assert snapshot.status is None
    assert snapshot.flag_state_code == 777
    assert snapshot.run_type_code == 888


@pytest.mark.parametrize("series", [1, 2, 3])
def test_naive_schedule_times_and_unknown_session_kinds(series):
    race = parse_schedule(fixture("schedule"), series, year=2026)[0]
    assert race.series_id == series
    assert race.start_time == datetime(2026, 10, 25, 18, tzinfo=UTC)
    assert all(session.start_time is not None for session in race.sessions)
    assert race.sessions[0].kind is None
    assert race.sessions[0].run_type_code == 0
    assert race.sessions[1].kind == "race"


def test_unmatched_session_race_is_preserved_and_local_zone_is_not_guessed():
    basic = parse_schedule(fixture("schedule"), 1, year=2026)
    details = parse_schedule_feed(fixture("sessions"), 1, 2026)
    merged = merge_schedule(basic, details)
    assert {race.race_id for race in merged} == {99051, 99059}
    assert all(
        race.start_time == datetime(2026, 10, 25, 18, tzinfo=UTC) for race in merged
    )
    assert all(
        session.end_time is not None for race in merged for session in race.sessions
    )
    assert parse_tracks(fixture("tracks"))[0].track_id == merged[0].track_id


def test_numeric_team_values_are_preserved_without_claiming_a_name_or_join():
    numeric, textual = parse_drivers(fixture("drivers"))
    assert numeric.team is None
    assert numeric.associations[0].team_raw == "88021"
    assert numeric.series_ids == ()
    assert textual.team == "Example Team"
    assert textual.associations[0].team_raw == "Example Team"
    assert textual.series_ids == ()


async def test_conflicting_schedule_tracks_do_not_replace_valid_basic_race():
    payload = fixture("sessions")
    payload[0]["track_id"] = 99082
    client, session = client_with(
        Response(body=json.dumps(fixture("schedule")).encode()),
        Response(body=json.dumps(payload).encode()),
    )
    provider = CFProvider(session)
    provider.api = client
    races = await provider.async_get_schedule(2026, 1)
    assert len(races) == 1
    assert races[0].track_id == 99081
    assert provider.schedule_details_failed == {(2026, 1)}
    assert provider.parse_results["sessions:2026:1"] == "context_conflict"
    assert session.get.call_count == 2


@pytest.mark.parametrize("series", [2, 3])
async def test_schedule_diagnostic_parse_results_are_series_scoped(series):
    payload = fixture("schedule")
    payload["series_1"][0]["series_id"] = 2
    client, session = client_with(
        Response(body=json.dumps(payload).encode()),
        Response(body=b"[]"),
        Response(body=b"[]"),
    )
    provider = CFProvider(session)
    provider.api = client
    with pytest.raises(SchemaError):
        await provider.async_get_schedule(2026, 1)
    assert await provider.async_get_schedule(2026, series)
    assert provider.parse_results["basic:2026:1"] == "invalid"
    assert provider.parse_results[f"basic:2026:{series}"] == "parsed"
    assert session.get.call_count == 3  # basic body is shared/cached


async def test_json_success_is_distinct_from_expected_session_parse_failure():
    client, session = client_with(Response(body=b'{"series_id":99,"race_id":99051}'))
    provider = CFProvider(session)
    provider.api = client
    with pytest.raises(SchemaError):
        await provider.async_get_live()
    assert client.diagnostics()[LIVE_FEED]["http_status"] == 200
    assert client.diagnostics()[LIVE_FEED]["json_status"] == "valid"
    assert provider.parse_results[LIVE_FEED] == "invalid"


def test_cross_series_rows_and_optional_failures_do_not_cross_wire_live_data():
    payload = fixture("live")
    payload["series_id"] = 2
    payload["vehicles"][0]["pit_stops"] = "malformed"
    payload["stage"] = []
    snapshot = parse_live(payload)
    assert snapshot.series_id == 2
    assert snapshot.leaderboard.by_driver[99011].pits_failed
    assert snapshot.stage_failed
    assert snapshot.flag == "yellow"
    assert snapshot.lap == 42
    assert snapshot.leaderboard.leader.driver_id == 99011
    bad = copy.deepcopy(fixture("sessions"))
    bad[0]["series_id"] = 2
    with pytest.raises(SchemaError):
        parse_schedule_feed(bad, 1, 2026)
