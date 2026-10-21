"""Verify the supported structural contract with tiny handmade responses."""

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from custom_components.nascar_race_center.models import (
    SchemaError,
    parse_live,
    parse_schedule,
)
from custom_components.nascar_race_center.provider import DemoProvider

FIXTURES = Path(__file__).parent / "fixtures" / "nascar"


def test_schedule_shapes_timezone_and_missing_fields() -> None:
    """Known fields normalize; optional omissions do not invent observations."""
    payload = json.loads((FIXTURES / "schedule.json").read_text())
    races = parse_schedule(payload, 1)
    assert races[0].race_id == 9001
    assert races[0].start_time == datetime(2026, 11, 1, 19, 30, tzinfo=UTC)
    assert races[1].start_time is None
    assert races[1].track is None
    assert parse_schedule(payload, 2)[0].series_id == 2
    assert parse_schedule(payload, 3) == ()


@pytest.mark.parametrize("payload", [None, [], {}, {"series_1": {}}, {"series_2": []}])
def test_unknown_schedule_envelope_is_not_empty(payload: object) -> None:
    """Schema drift is distinguishable from a valid empty season list."""
    with pytest.raises(SchemaError):
        parse_schedule(payload, 1)


@pytest.mark.parametrize(
    "identity",
    [
        {"race_id": None, "series_id": 1, "race_name": "Example"},
        {"race_id": 1, "series_id": 2, "race_name": "Example"},
        {"race_id": True, "series_id": 1, "race_name": "Example"},
        {"race_id": 1, "series_id": 1, "race_name": ""},
    ],
)
def test_invalid_schedule_identity(identity: dict[str, object]) -> None:
    """Never cross-wire national series or assign entities unstable identities."""
    with pytest.raises(SchemaError):
        parse_schedule({"series_1": [identity]}, 1)


def test_rescheduled_time_replaces_previous_time() -> None:
    """The upstream supplied time is authoritative, not fixed after first load."""
    row = {
        "race_id": 9001,
        "series_id": 1,
        "race_name": "Example",
        "date_scheduled": "2026-11-01T18:00:00Z",
    }
    before = parse_schedule({"series_1": [row]}, 1)[0]
    row["date_scheduled"] = "2026-11-02T18:00:00Z"
    after = parse_schedule({"series_1": [row]}, 1)[0]
    assert before.race_id == after.race_id
    assert before.start_time != after.start_time


@pytest.mark.parametrize(
    "value", ["2026-11-01T12:30:00", "2026-11-01", "not a date", "", None]
)
def test_unproven_timezone_is_unknown(value: object) -> None:
    """A timezone cannot be inferred from the feed field name alone."""
    races = parse_schedule(
        {
            "series_1": [
                {
                    "race_id": 1,
                    "series_id": 1,
                    "race_name": "Example",
                    "date_scheduled": value,
                }
            ]
        },
        1,
    )
    assert races[0].start_time is None


def test_live_shapes_and_source_time() -> None:
    """Live fields retain source time separately from transport observation."""
    snapshot = parse_live(json.loads((FIXTURES / "live.json").read_text()))
    assert snapshot is not None
    assert snapshot.series_id == 1
    assert snapshot.race_id == 9001
    assert snapshot.status == "race"
    assert snapshot.flag == "yellow"
    assert snapshot.lap == 42
    assert snapshot.source_updated_at == datetime(2026, 11, 1, 20, tzinfo=UTC)
    assert snapshot.observed_at.tzinfo == UTC


def test_missing_or_unknown_live_fields_remain_unknown() -> None:
    """Missing/novel optional data does not disable the session identity."""
    snapshot = parse_live(
        {"series_id": 2, "race_id": 9101, "run_type": 99, "flag_state": 999}
    )
    assert snapshot is not None
    assert snapshot.status is None
    assert snapshot.flag is None
    assert snapshot.lap is None
    assert snapshot.source_updated_at is None


def test_mocked_no_session_differs_from_unknown_envelope() -> None:
    """Null is explicitly empty; undocumented envelopes require investigation."""
    assert parse_live(None) is None
    with pytest.raises(SchemaError):
        parse_live({})
    with pytest.raises(SchemaError):
        parse_live({"series_id": 99, "race_id": 9001})


async def test_demo_provider_is_offline_and_series_aware() -> None:
    """A fresh provider can reproduce the same fictional schedule offline."""
    first = DemoProvider()
    second = DemoProvider()
    assert await first.async_get_schedule(2027, 1) == await second.async_get_schedule(
        2027, 1
    )
    assert (await first.async_get_schedule(2027, 3))[0].series_id == 3
    assert await first.async_get_live() is None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-11-01T12:30:00-05:00", datetime(2026, 11, 1, 17, 30, tzinfo=UTC)),
        ("2026-11-01T12:30:00+02:00", datetime(2026, 11, 1, 10, 30, tzinfo=UTC)),
        ("0001-01-01T00:00:00+01:00", None),
        ("9999-12-31T23:59:59-01:00", None),
    ],
)
def test_explicit_schedule_offsets_and_utc_range(value, expected) -> None:
    """Respect supplied offsets and reject timestamps outside UTC's range."""
    races = parse_schedule(
        {
            "series_1": [
                {
                    "race_id": 1,
                    "series_id": 1,
                    "race_name": "Example",
                    "date_scheduled": value,
                }
            ]
        },
        1,
    )
    assert races[0].start_time == expected
