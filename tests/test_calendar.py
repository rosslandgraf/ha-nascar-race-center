"""Native Home Assistant calendars preserve identity and conservative timing."""

from dataclasses import replace
from datetime import UTC, date, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.nascar_race_center.calendar import NascarSeriesCalendar
from custom_components.nascar_race_center.const import (
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    PROVIDER_DEMO,
)
from custom_components.nascar_race_center.coordinator import ScheduleData
from custom_components.nascar_race_center.models import Race, Session
from custom_components.nascar_race_center.reference import Track
from custom_components.nascar_race_center.reference_coordinator import ReferenceData


async def setup_calendar(
    hass: HomeAssistant, races: tuple[Race, ...], series: tuple[int, ...] = (1,)
) -> tuple[MockConfigEntry, Mock, dict[int, NascarSeriesCalendar]]:
    """Load real HA platforms while mocking only the NASCAR provider boundary."""
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        side_effect=lambda year, series_id: tuple(
            race for race in races if race.series_id == series_id
        )
    )
    provider.async_get_live = AsyncMock(return_value=None)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_PROVIDER: PROVIDER_DEMO, CONF_SERIES: list(map(str, series))},
    )
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    calendars = {}
    for series_id in series:
        entity_id = er.async_get(hass).async_get_entity_id(
            "calendar", DOMAIN, f"{entry.entry_id}_{series_id}_calendar"
        )
        assert entity_id is not None
        entity = hass.data["calendar"].get_entity(entity_id)
        assert isinstance(entity, NascarSeriesCalendar)
        calendars[series_id] = entity
    return entry, provider, calendars


def session(
    kind: str, start: str, end: str | None = None, *, status: str | None = None
) -> Session:
    """Create a normalized handmade session, not a captured NASCAR response."""
    return Session(
        kind,
        kind.capitalize(),
        kind=kind,
        start_time=datetime.fromisoformat(start),
        end_time=datetime.fromisoformat(end) if end else None,
        status=status,
    )


async def test_native_calendar_service_routes_all_three_series(
    hass: HomeAssistant,
) -> None:
    """Users can query per-series sessions through the native calendar service."""
    races = tuple(
        Race(
            series_id,
            100 + series_id,
            f"Synthetic series {series_id}",
            track=f"Test track {series_id}",
            season=2027,
            sessions=(session("race", "2027-02-01T19:00Z", "2027-02-01T22:00Z"),),
        )
        for series_id in (1, 2, 3)
    )
    _, provider, calendars = await setup_calendar(hass, races, (1, 2, 3))
    provider.async_get_schedule.reset_mock()
    for series_id, calendar in calendars.items():
        result = await hass.services.async_call(
            "calendar",
            "get_events",
            {
                "entity_id": calendar.entity_id,
                "start_date_time": "2027-02-01T00:00:00+00:00",
                "end_date_time": "2027-02-02T00:00:00+00:00",
            },
            blocking=True,
            return_response=True,
        )
        events = result[calendar.entity_id]["events"]
        assert len(events) == 2
        assert all(f"Synthetic series {series_id}" in row["summary"] for row in events)
        assert all(f"Test track {series_id}" in row["location"] for row in events)
        assert calendar.supported_features == 0
    provider.async_get_schedule.assert_not_awaited()


@pytest.mark.parametrize(
    ("start", "end", "local_start", "local_end", "query"),
    [
        (
            "2027-03-14T06:30Z",
            "2027-03-14T07:30Z",
            "01:30",
            "03:30",
            "2027-03-14T07:00Z",
        ),
        (
            "2027-11-07T05:30Z",
            "2027-11-07T06:30Z",
            "01:30",
            "01:30",
            "2027-11-07T06:00Z",
        ),
    ],
)
async def test_dst_uses_real_elapsed_time_and_local_display(
    hass: HomeAssistant,
    start: str,
    end: str,
    local_start: str,
    local_end: str,
    query: str,
) -> None:
    """Spring gaps and repeated fall hours preserve the explicit UTC bounds."""
    await hass.config.async_set_time_zone("America/New_York")
    race = Race(1, 1, "DST fixture", sessions=(session("race", start, end),))
    _, _, calendars = await setup_calendar(hass, (race,))
    at = datetime.fromisoformat(query)
    events = await calendars[1].async_get_events(hass, at, at + timedelta(minutes=1))
    timed = next(event for event in events if not event.all_day)
    assert timed.start == datetime.fromisoformat(start)
    assert timed.end == datetime.fromisoformat(end)
    assert timed.end - timed.start == timedelta(hours=1)
    assert timed.start_datetime_local.strftime("%H:%M") == local_start
    assert timed.end_datetime_local.strftime("%H:%M") == local_end


async def test_weekend_spans_year_boundary_and_queries_overlap(
    hass: HomeAssistant,
) -> None:
    """Multi-day date markers and exact sessions remain queryable in January."""
    await hass.config.async_set_time_zone("UTC")
    race = Race(
        1,
        10,
        "Year boundary",
        season=2026,
        sessions=(
            session("practice", "2026-12-31T20:00Z", "2026-12-31T21:00Z"),
            session("qualifying", "2027-01-01T12:00Z", "2027-01-01T13:00Z"),
            session("race", "2027-01-01T23:00Z", "2027-01-02T00:00Z"),
        ),
    )
    _, _, calendars = await setup_calendar(hass, (race,))
    events = await calendars[1].async_get_events(
        hass, datetime(2027, 1, 1, tzinfo=UTC), datetime(2027, 1, 2, tzinfo=UTC)
    )
    assert len(events) == 3
    weekend = next(event for event in events if event.uid.endswith(":weekend"))
    assert weekend.start == date(2026, 12, 31)
    assert weekend.end == date(2027, 1, 2)
    assert "derived from published session dates" in weekend.description
    assert all("Practice" not in event.summary for event in events)


async def test_month_boundary_exclusive_bounds_and_overlapping_sessions(
    hass: HomeAssistant,
) -> None:
    """Events started before the requested month are included until their end."""
    race = Race(
        1,
        10,
        "Month boundary",
        sessions=(
            session("practice", "2027-01-31T23:00Z", "2027-02-01T02:00Z"),
            session("qualifying", "2027-02-01T01:00Z", "2027-02-01T03:00Z"),
            session("race", "2027-02-01T03:00Z", "2027-02-01T04:00Z"),
        ),
    )
    _, _, calendars = await setup_calendar(hass, (race,))
    events = await calendars[1].async_get_events(
        hass, datetime(2027, 2, 1, 1, tzinfo=UTC), datetime(2027, 2, 1, 3, tzinfo=UTC)
    )
    assert {event.uid.rsplit(":", 1)[1] for event in events} == {
        "practice",
        "qualifying",
        "weekend",
    }
    at_end = await calendars[1].async_get_events(
        hass, datetime(2027, 2, 1, 4, tzinfo=UTC), datetime(2027, 2, 2, tzinfo=UTC)
    )
    assert all(event.all_day for event in at_end)


@pytest.mark.parametrize("end", [None, "2027-02-01T02:00", "2027-02-01T00:00Z"])
async def test_unknown_duration_is_labeled_local_date_marker(
    hass: HomeAssistant, end: str | None
) -> None:
    """Unknown, naive or reversed ends never fabricate a timed duration."""
    await hass.config.async_set_time_zone("America/New_York")
    race = Race(
        1,
        10,
        "Unknown duration",
        sessions=(session("race", "2027-02-01T01:00Z", end),),
    )
    _, _, calendars = await setup_calendar(hass, (race,))
    events = await calendars[1].async_get_events(
        hass, datetime(2027, 1, 31, tzinfo=UTC), datetime(2027, 2, 2, tzinfo=UTC)
    )
    marker = next(event for event in events if not event.uid.endswith(":weekend"))
    assert marker.all_day
    assert marker.start == date(2027, 1, 31)
    assert marker.end == date(2027, 2, 1)
    assert "duration unconfirmed" in marker.summary
    assert "2027-01-31T20:00:00-05:00" in marker.description
    assert "does not mean the session lasts all day" in marker.description


async def test_unknown_timestamps_and_canceled_sessions_are_omitted(
    hass: HomeAssistant,
) -> None:
    """A canceled race-kind session cannot be replaced by a phantom race."""
    known = datetime(2027, 2, 1, 20, tzinfo=UTC)
    races = (
        Race(
            1,
            1,
            "Partial weekend",
            start_time=known,
            sessions=(
                Session("unknown", "Unknown", kind="practice"),
                session("qualifying", "2027-02-01T12:00"),
                session("race", "2027-02-01T20:00Z", status="canceled"),
            ),
        ),
        Race(1, 2, "Canceled weekend", start_time=known, status="cancelled"),
        Race(1, 3, "No dates"),
    )
    _, _, calendars = await setup_calendar(hass, races)
    assert (
        await calendars[1].async_get_events(
            hass, known - timedelta(days=1), known + timedelta(days=1)
        )
        == []
    )


async def test_postponed_event_updates_keep_uid_and_remove_old_time(
    hass: HomeAssistant,
) -> None:
    """Moving a session across year/month boundaries replaces its stable event."""
    race = Race(
        1,
        10,
        "Rescheduled event",
        season=2026,
        sessions=(session("race", "2026-12-31T22:00Z", "2026-12-31T23:00Z"),),
    )
    entry, _, calendars = await setup_calendar(hass, (race,))
    calendar = calendars[1]
    before = calendar._events()
    moved = replace(
        race,
        status="postponed",
        sessions=(
            replace(
                race.sessions[0],
                start_time=datetime(2027, 1, 1, 22, tzinfo=UTC),
                end_time=datetime(2027, 1, 1, 23, tzinfo=UTC),
            ),
        ),
    )
    entry.runtime_data.schedule.async_set_updated_data(
        ScheduleData({1: (moved,)}, frozenset(), {1: dt_util.utcnow()})
    )
    await hass.async_block_till_done()
    after = calendar._events()
    assert {event.uid for event in before} == {event.uid for event in after}
    assert all("Status: postponed" in event.description for event in after)
    assert (
        await calendar.async_get_events(
            hass, datetime(2026, 12, 31, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC)
        )
        == []
    )


async def test_calendar_falls_back_to_race_start_without_session_data(
    hass: HomeAssistant,
) -> None:
    """Phase 1 race-only models remain usable without imaginary session bounds."""
    start = datetime(2027, 2, 1, 20, tzinfo=UTC)
    _, _, calendars = await setup_calendar(hass, (Race(1, 10, "Legacy race", start),))
    events = await calendars[1].async_get_events(
        hass, start - timedelta(days=1), start + timedelta(days=1)
    )
    assert len(events) == 2
    assert all(event.all_day for event in events)
    assert any("duration unconfirmed" in event.summary for event in events)


async def test_calendar_does_not_serve_failed_schedule_as_current(
    hass: HomeAssistant,
) -> None:
    """Retained data remains diagnostic rather than a successful calendar fetch."""
    now = dt_util.utcnow()
    entry, _, calendars = await setup_calendar(hass, (Race(1, 10, "Outage", now),))
    entry.runtime_data.schedule.async_set_updated_data(
        ScheduleData({1: (Race(1, 10, "Outage", now),)}, frozenset({1}), {1: now})
    )
    await hass.async_block_till_done()
    assert hass.states.get(calendars[1].entity_id).state == STATE_UNAVAILABLE
    with pytest.raises(HomeAssistantError, match="unavailable"):
        await calendars[1].async_get_events(hass, now, now + timedelta(days=1))


async def test_failed_current_season_does_not_hide_healthy_next_season(
    hass: HomeAssistant,
) -> None:
    """Retained failed-season data never appears as current in a usable calendar."""
    first = Race(
        1,
        10,
        "Failed season",
        season=2026,
        sessions=(session("race", "2026-12-31T20:00Z", "2026-12-31T21:00Z"),),
    )
    second = Race(
        1,
        11,
        "Healthy next season",
        season=2027,
        sessions=(session("race", "2027-01-01T20:00Z", "2027-01-01T21:00Z"),),
    )
    entry, _, calendars = await setup_calendar(hass, (first, second))
    entry.runtime_data.schedule.async_set_updated_data(
        ScheduleData(
            {1: (first, second)},
            frozenset(),
            {1: dt_util.utcnow()},
            failed_seasons={1: frozenset({2026})},
        )
    )
    await hass.async_block_till_done()
    assert calendars[1].available
    events = await calendars[1].async_get_events(
        hass, datetime(2026, 12, 30, tzinfo=UTC), datetime(2027, 1, 3, tzinfo=UTC)
    )
    assert len(events) == 2
    assert all("Healthy next season" in event.summary for event in events)


async def test_verified_basic_time_survives_missing_detailed_race_timestamp(
    hass: HomeAssistant,
) -> None:
    """Unpublished detailed timestamps do not erase a known season-list time."""
    await hass.config.async_set_time_zone("UTC")
    start = datetime(2027, 2, 1, 20, tzinfo=UTC)
    race = Race(
        1,
        10,
        "Basic time",
        start_time=start,
        sessions=(Session("stable-race", "Race", kind="race"),),
    )
    _, _, calendars = await setup_calendar(hass, (race,))
    events = await calendars[1].async_get_events(
        hass, start - timedelta(days=1), start + timedelta(days=1)
    )
    race_event = next(event for event in events if event.uid.endswith(":stable-race"))
    assert "season race schedule" in race_event.description
    assert "2027-02-01T20:00:00" in race_event.description


@pytest.mark.parametrize("failed", [True, False])
async def test_track_enrichment_updates_without_disabling_calendar_on_outage(
    hass: HomeAssistant, failed: bool
) -> None:
    """Failed or expired track metadata is omitted while race data remains usable."""
    now = dt_util.utcnow()
    race = Race(
        1, 10, "Venue fixture", now + timedelta(days=1), "Schedule track", track_id=7
    )
    entry, _, calendars = await setup_calendar(hass, (race,))
    reference = entry.runtime_data.reference
    tracks = {7: Track(7, "Reference track", city="Fixture City", state="Test State")}
    reference.async_set_updated_data(
        ReferenceData({}, tracks, frozenset(), {"tracks": now})
    )
    await hass.async_block_till_done()
    events = calendars[1]._events()
    assert all("Fixture City, Test State" in event.location for event in events)
    reference.async_set_updated_data(
        ReferenceData(
            {},
            tracks,
            frozenset({"tracks"}) if failed else frozenset(),
            {"tracks": now - timedelta(days=8) if not failed else now},
        )
    )
    await hass.async_block_till_done()
    assert calendars[1].available
    events = calendars[1]._events()
    assert all(event.location == "Schedule track" for event in events)
    assert all("Fixture City" not in event.description for event in events)


@pytest.mark.parametrize(
    ("zone", "start"),
    [
        ("America/New_York", datetime.min.replace(tzinfo=UTC)),
        ("America/New_York", datetime.max.replace(tzinfo=UTC)),
        ("Asia/Tokyo", datetime.min.replace(tzinfo=UTC)),
        ("Asia/Tokyo", datetime.max.replace(tzinfo=UTC)),
    ],
)
async def test_extreme_known_times_that_cannot_form_local_events_are_omitted(
    hass: HomeAssistant, zone: str, start: datetime
) -> None:
    """Offset-aware parser values must not overflow HA's local calendar display."""
    await hass.config.async_set_time_zone(zone)
    race = Race(
        1,
        10,
        "Range fixture",
        sessions=(Session("race", "Race", kind="race", start_time=start),),
    )
    _, _, calendars = await setup_calendar(hass, (race,))
    assert calendars[1]._events() == []


async def test_session_start_and_end_update_locally_and_unload_cleans_alarms(
    hass: HomeAssistant, freezer
) -> None:
    """Overlapping weekend markers do not hide timed session starts or leak tasks."""
    freezer.move_to("2026-10-20T12:00:00Z")
    race = Race(
        1,
        10,
        "Local transitions",
        sessions=(
            session("practice", "2026-10-20T12:01Z", "2026-10-20T12:02Z"),
            session("qualifying", "2026-10-20T12:03Z", "2026-10-20T12:04Z"),
            session("race", "2026-10-20T12:05Z", "2026-10-20T12:06Z"),
        ),
    )
    entry, provider, calendars = await setup_calendar(hass, (race,))
    calendar = calendars[1]
    assert "Race weekend" in hass.states.get(calendar.entity_id).attributes["message"]
    provider.async_get_schedule.reset_mock()
    for when, expected in [
        ("2026-10-20T12:01:01Z", "Practice"),
        ("2026-10-20T12:02:01Z", "Race weekend"),
        ("2026-10-20T12:03:01Z", "Qualifying"),
        ("2026-10-20T12:04:01Z", "Race weekend"),
    ]:
        freezer.move_to(when)
        async_fire_time_changed(hass, dt_util.utcnow())
        await hass.async_block_till_done()
        assert expected in hass.states.get(calendar.entity_id).attributes["message"]
    assert calendar._unsub_overlap is not None
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert calendar._unsub_overlap is None
    assert calendar._alarm_unsubs is None
    freezer.move_to("2026-10-20T12:07:00Z")
    async_fire_time_changed(hass, dt_util.utcnow())
    await hass.async_block_till_done()
    provider.async_get_schedule.assert_not_awaited()


async def test_overlapping_sessions_advance_when_shorter_session_starts_and_ends(
    hass: HomeAssistant, freezer
) -> None:
    """A shorter session can take priority during an already active session."""
    freezer.move_to("2026-10-20T12:00:00Z")
    race = Race(
        1,
        10,
        "Overlapping sessions",
        sessions=(
            session("practice", "2026-10-20T12:01Z", "2026-10-20T12:05Z"),
            session("qualifying", "2026-10-20T12:02Z", "2026-10-20T12:03Z"),
        ),
    )
    entry, provider, calendars = await setup_calendar(hass, (race,))
    calendar = calendars[1]
    provider.async_get_schedule.reset_mock()
    for when, expected in (
        ("2026-10-20T12:01:01Z", "Practice"),
        ("2026-10-20T12:02:01Z", "Qualifying"),
        ("2026-10-20T12:03:01Z", "Practice"),
        ("2026-10-20T12:05:01Z", "Race weekend"),
    ):
        freezer.move_to(when)
        async_fire_time_changed(hass, dt_util.utcnow())
        await hass.async_block_till_done()
        assert expected in hass.states.get(calendar.entity_id).attributes["message"]
    provider.async_get_schedule.assert_not_awaited()
    assert await hass.config_entries.async_unload(entry.entry_id)
