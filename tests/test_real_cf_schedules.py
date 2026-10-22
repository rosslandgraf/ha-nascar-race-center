"""Owner-reported field shapes; minimal handmade rows, never CF network captures."""

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from zoneinfo import ZoneInfo

import pytest
from homeassistant.util import dt as dt_util
from test_calendar import setup_calendar

from custom_components.nascar_race_center.dashboard_views import bootstrap
from custom_components.nascar_race_center.models import (
    Race,
    merge_schedule,
    parse_live,
    parse_schedule,
    parse_schedule_feed,
    schedule_quality,
)
from custom_components.nascar_race_center.provider import CFProvider


def row(series=1, kind=2, start="2026-10-23T16:30:00", end="2026-10-23T18:00:00"):
    return {
        "series_id": series,
        "race_id": 9901,
        "race_name": "Synthetic future weekend",
        "track_id": 99001,
        "track_name": "Synthetic track",
        "run_type": kind,
        "event_name": {1: "Practice", 2: "Qualifying (Impound)", 3: "Race"}[kind],
        "start_time_utc": start,
        "end_time_utc": end,
        "start_time": "2026-10-23T11:30:00",
    }


@pytest.mark.parametrize("series", [1, 2, 3])
@pytest.mark.parametrize(
    "zone,hour",
    [("America/New_York", 12), ("America/Chicago", 11), ("America/Los_Angeles", 9)],
)
def test_named_utc_contract_is_independent_of_track_and_server_zone(series, zone, hour):
    session = parse_schedule_feed([row(series)], series, 2026)[0].sessions[0]
    assert session.start_time == datetime(2026, 10, 23, 16, 30, tzinfo=UTC)
    assert session.end_time == datetime(2026, 10, 23, 18, tzinfo=UTC)
    assert session.start_time.astimezone(ZoneInfo(zone)).hour == hour
    # The same bare clock in the live feed is still unknown.
    live = parse_live(
        {"series_id": series, "race_id": 9901, "time_of_day_os": "2026-10-23T16:30:00"}
    )
    assert live.source_updated_at is None


@pytest.mark.parametrize("series", [1, 2, 3])
@pytest.mark.parametrize(
    "start,end,seconds",
    [
        ("2026-03-08T06:30:00", "2026-03-08T07:30:00", 3600),
        ("2026-11-01T05:30:00", "2026-11-01T06:30:00", 3600),
        ("2026-11-05T23:30:00", "2026-11-06T00:20:00", 3000),
        ("2026-11-05T18:30:00-05:00", "2026-11-05T19:20:00-05:00", 3000),
    ],
)
def test_dst_standard_time_explicit_offsets_and_cross_midnight(
    series, start, end, seconds
):
    session = parse_schedule_feed([row(series, 1, start, end)], series, 2026)[
        0
    ].sessions[0]
    assert (session.end_time - session.start_time).total_seconds() == seconds
    assert session.start_time.utcoffset() == timedelta(0)
    if "11-05" in start:
        assert session.start_time.astimezone(ZoneInfo("America/New_York")).hour == 18


@pytest.mark.parametrize("series", [1, 2, 3])
def test_year_one_is_unknown_not_a_date_or_duration_and_quality_is_bounded(series):
    rows = [
        dict(
            row(series, 1),
            event_name=f"Synthetic session {index}",
            end_time_utc="0001-01-01T00:00:00",
        )
        for index in range(26)
    ]
    races = parse_schedule_feed(rows, series, 2026)
    assert all(
        s.start_time is not None and s.end_time is None for s in races[0].sessions
    )
    quality = schedule_quality(rows, races, series, detailed=True)
    assert quality["unknown_session_ends"] == 26
    assert quality["timestamp_reasons"]["end_time_utc"] == {"unknown_year_one": 26}
    assert "Synthetic session" not in repr(quality)
    for value in ["0001-01-01T00:00:00Z", "0001-01-01T00:00:00", "2026-10-23", None]:
        assert (
            parse_schedule_feed([row(series, 1, value)], series, 2026)[0]
            .sessions[0]
            .start_time
            is None
        )


@pytest.mark.parametrize("series", [1, 2, 3])
def test_basic_utc_race_session_can_fill_an_ambiguous_basic_date(series):
    nested = {
        "event_name": "Race",
        "run_type": 3,
        "start_time_utc": "2026-10-25T18:00:00",
    }
    payload = {
        f"series_{series}": [
            {
                "race_id": 9901,
                "series_id": series,
                "race_name": "Synthetic",
                "date_scheduled": "2026-10-25T13:00:00",
                "schedule": [nested],
            }
        ]
    }
    race = parse_schedule(payload, series, year=2026)[0]
    assert race.start_time == datetime(2026, 10, 25, 18, tzinfo=UTC)
    # No UTC session: never guess that date_scheduled/local start_time is Eastern.
    payload[f"series_{series}"][0]["schedule"] = []
    assert parse_schedule(payload, series, year=2026)[0].start_time is None


@pytest.mark.parametrize("series", [1, 2, 3])
async def test_detail_only_weekend_survives_basic_outage_and_rescheduling(series):
    provider = CFProvider(MagicMock())
    rows = [
        row(series, 3, "2026-10-25T18:00:00", "0001-01-01T00:00:00"),
        row(series, 2),
        row(series, 1, "2026-10-23T15:00:00"),
    ]
    provider.api.async_get_json = AsyncMock(side_effect=[{}, rows])
    races = await provider.async_get_schedule(2026, series)
    assert len(races) == 1
    assert [s.kind for s in races[0].sessions] == ["practice", "qualifying", "race"]
    revised = [dict(r) for r in reversed(rows)]
    revised[0]["start_time_utc"] = "2026-10-24T15:00:00"
    after = parse_schedule_feed(revised, series, 2026)[0]
    assert {s.session_id for s in after.sessions} == {
        s.session_id for s in races[0].sessions
    }
    basic = (
        Race(
            series,
            9902,
            "Independent basic race",
            datetime(2026, 11, 1, 18, tzinfo=UTC),
            season=2026,
        ),
    )
    assert {r.race_id for r in merge_schedule(basic, races)} == {9901, 9902}


@pytest.mark.parametrize("series", [1, 2, 3])
@pytest.mark.parametrize(
    "zone,hour",
    [("America/New_York", 12), ("America/Chicago", 11), ("America/Los_Angeles", 9)],
)
async def test_native_calendar_and_bootstrap_choose_future_activity(
    hass, freezer, series, zone, hour
):
    freezer.move_to("2026-10-22T12:00:00Z")
    await hass.config.async_set_time_zone(zone)
    races = parse_schedule_feed(
        [
            row(series, 3, "2026-10-25T18:00:00", "2026-10-25T21:00:00"),
            row(series, 2),
            row(series, 1, "2026-10-23T15:00:00", "2026-10-23T16:00:00"),
        ],
        series,
        2026,
    )
    old = replace(
        races[0],
        race_id=9900,
        name="Historical only",
        start_time=datetime(2026, 10, 1, 18, tzinfo=UTC),
        sessions=(),
    )
    entry, provider, calendars = await setup_calendar(hass, (races[0], old), (series,))
    next_race = entry.runtime_data.schedule.next_race(series)
    assert next_race.race_id == 9901
    data = bootstrap(entry)
    assert data["next_activity"]["session"]["kind"] == "practice"
    assert data["upcoming"][0]["race_id"] == "9901"
    assert all(r["name"] != "Historical only" for r in data["upcoming"])
    events = await calendars[series].async_get_events(
        hass, datetime(2026, 10, 23, tzinfo=UTC), datetime(2026, 10, 24, tzinfo=UTC)
    )
    qualifying = next(e for e in events if "Qualifying" in e.summary)
    assert qualifying.start.hour == 16
    assert dt_util.as_local(qualifying.start).hour == hour
    assert qualifying.end - qualifying.start == timedelta(minutes=90)
    # Canceled normalized sessions are omitted; source status fields remain unguessed.
    canceled = replace(
        races[0],
        sessions=tuple(replace(s, status="canceled") for s in races[0].sessions),
    )
    assert calendars[series]._session_event(canceled, canceled.sessions[0]) is None
    provider.async_get_schedule.reset_mock()
    assert entry.runtime_data.schedule.usable_races(series)
    assert not provider.async_get_schedule.called


@pytest.mark.parametrize("series", [1, 2, 3])
def test_minute_precision_offsets_and_naive_utc_are_preserved(series):
    for start in ["2026-11-05T23:30Z", "2026-11-05T18:30-05:00", "2026-11-05T23:30"]:
        session = parse_schedule_feed([row(series, 1, start, None)], series, 2026)[
            0
        ].sessions[0]
        assert session.start_time == datetime(2026, 11, 5, 23, 30, tzinfo=UTC)


async def test_next_race_uses_minimum_and_bootstrap_skips_unknown_run_activity(
    hass, freezer
):
    freezer.move_to("2026-10-22T12:00:00Z")
    upcoming = parse_schedule_feed(
        [
            row(1, 3, "2026-10-25T18:00:00"),
            row(1, 1, "2026-10-23T15:00:00"),
        ],
        1,
        2026,
    )[0]
    extra = replace(
        upcoming.sessions[0],
        session_id="garage",
        kind=None,
        start_time=datetime(2026, 10, 23, 12, tzinfo=UTC),
    )
    upcoming = replace(upcoming, sessions=(extra, *upcoming.sessions))
    later = replace(
        upcoming,
        race_id=9903,
        start_time=datetime(2026, 11, 1, 18, tzinfo=UTC),
        sessions=(),
    )
    completed = replace(
        upcoming,
        race_id=9904,
        start_time=datetime(2026, 10, 24, 18, tzinfo=UTC),
        sessions=(),
        status="completed",
    )
    entry, _, _ = await setup_calendar(hass, (later, completed, upcoming), (1,))
    assert entry.runtime_data.schedule.next_race(1).race_id == 9901
    assert bootstrap(entry)["next_activity"]["session"]["kind"] == "practice"
    assert any(s.kind is None for s in upcoming.sessions)
