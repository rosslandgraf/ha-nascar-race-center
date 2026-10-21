"""Handmade scoring contracts, optional drift and immutable complete fields."""

import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from custom_components.nascar_race_center.models import parse_live

FIXTURE = Path(__file__).parent / "fixtures" / "nascar" / "live_timing.json"


def timing_payload():
    """Load a fresh synthetic field; no source captures or network calls."""
    return json.loads(FIXTURE.read_text())


def test_reported_field_order_identity_and_supported_metrics():
    snapshot = parse_live(timing_payload())
    assert snapshot.session_key == (1, 99001, 7)
    assert snapshot.run_name == "Synthetic Race"
    assert snapshot.total_laps == 100
    assert snapshot.laps_remaining == 58
    assert snapshot.elapsed_seconds == 1234
    board = snapshot.leaderboard
    assert [driver.driver_id for driver in board.drivers] == [99001, 99002, 99003]
    assert board.reported_count == 3
    assert board.omitted_count == 0
    assert board.leader.driver_id == 99001
    driver = board.by_driver[99002]
    assert driver.car_number == "07"
    assert driver.position_change == 3
    assert driver.last_lap_time == 31.25
    assert driver.best_lap_time == 30.5
    assert driver.last_lap_speed == 172.8
    assert driver.best_lap_speed == 177.0
    assert driver.average_speed == 170.0
    assert driver.gap == 0.75
    assert driver.manufacturer == "Tyt"
    assert driver.running_status == "running"
    assert driver.is_on_track is True
    assert driver.laps_completed == 41
    assert driver.laps_led[0].start_lap == 5
    assert driver.laps_led[0].end_lap == 10
    assert board.by_driver[99003].running_status is None
    assert board.by_driver[99003].status_code == 99
    with pytest.raises(TypeError):
        board.by_driver[99002] = driver
    with pytest.raises(FrozenInstanceError):
        driver.position = 1


@pytest.mark.parametrize("series_id", [1, 2, 3])
def test_whole_national_field_and_session_replacement(series_id):
    payload = timing_payload()
    payload["series_id"] = series_id
    payload["vehicles"] = [
        {"driver": {"driver_id": driver_id}, "running_position": 41 - driver_id}
        for driver_id in range(1, 41)
    ]
    snapshot = parse_live(payload)
    assert snapshot.series_id == series_id
    assert len(snapshot.leaderboard.drivers) == 40
    assert snapshot.leaderboard.leader.driver_id == 40
    # No history survives into another race/run or a reduced field.
    payload.update(race_id=99002, run_id=8, lap_number=0, vehicles=[])
    next_snapshot = parse_live(payload)
    assert next_snapshot.session_key != snapshot.session_key
    assert next_snapshot.leaderboard.drivers == ()
    assert next_snapshot.lap == 0


@pytest.mark.parametrize(
    "vehicles", [{}, "unknown", None, [None], [{}], [True], [{}] * 101]
)
def test_optional_bad_field_keeps_independent_race_context(vehicles):
    payload = timing_payload()
    payload["vehicles"] = vehicles
    snapshot = parse_live(payload)
    assert snapshot.flag == "green"
    assert snapshot.lap == 42
    assert snapshot.leaderboard is None
    assert snapshot.leaderboard_failed


def test_absent_empty_and_partly_unidentified_fields_differ():
    payload = timing_payload()
    del payload["vehicles"]
    assert parse_live(payload).leaderboard is None
    assert not parse_live(payload).leaderboard_failed
    payload["vehicles"] = []
    assert parse_live(payload).leaderboard.reported_count == 0
    payload["vehicles"] = [
        {"driver": {"driver_id": True}, "vehicle_number": 1},
        {"driver": {"driver_id": "123"}, "vehicle_number": "00"},
        {"driver_id": 999, "vehicle_number": 9},
    ]
    board = parse_live(payload).leaderboard
    assert board.reported_count == 3
    assert board.omitted_count == 2
    assert list(board.by_driver) == [123]
    assert board.by_driver[123].car_number == "00"
    assert board.by_driver[123].position is None
    assert board.leader is None


def test_duplicate_driver_identity_fails_field_and_duplicate_ranks_hide_leader():
    payload = timing_payload()
    payload["vehicles"][0]["driver"]["driver_id"] = 99001
    assert parse_live(payload).leaderboard_failed
    payload = timing_payload()
    payload["vehicles"][0]["running_position"] = 1
    assert parse_live(payload).leaderboard.leader is None


@pytest.mark.parametrize("value", [True, None, {}, "bad", "NaN", float("inf"), 0, -1])
def test_optional_nonpositive_timing_remains_unknown(value):
    payload = timing_payload()
    payload["vehicles"][0].update(last_lap_time=value, best_lap_speed=value)
    driver = parse_live(payload).leaderboard.by_driver[99002]
    assert driver.last_lap_time is None
    assert driver.best_lap_speed is None
    assert driver.position == 2


def test_zero_gap_signed_gap_and_unknown_status_are_not_laps_or_retirement():
    payload = timing_payload()
    payload["vehicles"][0].update(delta=-2.5, status=8, is_on_track="false")
    board = parse_live(payload).leaderboard
    assert board.by_driver[99001].gap == 0.0
    assert board.by_driver[99002].gap == -2.5
    assert board.by_driver[99002].running_status is None
    assert board.by_driver[99002].is_on_track is None
    assert board.by_driver[99003].last_lap_time is None


@pytest.mark.parametrize(
    "intervals", [None, {}, [None], [{"start_lap": 9, "end_lap": 2}], [{}] * 1001]
)
def test_invalid_laps_led_are_unknown_not_zero(intervals):
    payload = timing_payload()
    payload["vehicles"][0]["laps_led"] = intervals
    assert parse_live(payload).leaderboard.by_driver[99002].laps_led is None


@pytest.mark.parametrize("timestamp", [1234567890, "2026-10-20T20:00:00", "bad", None])
def test_source_timestamp_semantics_are_not_inferred(timestamp):
    payload = timing_payload()
    payload["time_of_day_os"] = timestamp
    assert parse_live(payload).source_updated_at is None


def test_local_observation_time_does_not_change_model_equality():
    snapshot = parse_live(timing_payload())
    assert snapshot == replace(snapshot, observed_at=snapshot.source_updated_at)


async def test_conditional_live_cache_retains_source_time_and_reported_field():
    """304 and local cache hits are transport successes, not new observations."""
    from unittest.mock import MagicMock, patch

    from test_api import Response

    from custom_components.nascar_race_center.provider import CFProvider

    session = MagicMock()
    session.get.side_effect = [
        Response(body=FIXTURE.read_bytes(), headers={"ETag": '"timing-v1"'}),
        Response(status=304),
    ]
    provider = CFProvider(session)
    with patch("custom_components.nascar_race_center.api._monotonic", return_value=100):
        initial = await provider.async_get_live()
        cached = await provider.async_get_live()
    assert session.get.call_count == 1
    with patch("custom_components.nascar_race_center.api._monotonic", return_value=400):
        revalidated = await provider.async_get_live()
    assert session.get.call_count == 2
    assert (
        initial.source_updated_at
        == cached.source_updated_at
        == revalidated.source_updated_at
    )
    assert initial.leaderboard == revalidated.leaderboard
    assert session.get.call_args.kwargs["headers"]["If-None-Match"] == '"timing-v1"'
    session.close.assert_not_called()
