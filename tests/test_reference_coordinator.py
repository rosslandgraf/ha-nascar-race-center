"""Independent reference freshness, outage isolation and entry task ownership."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from test_init import demo_entry

from custom_components.nascar_race_center.const import DOMAIN
from custom_components.nascar_race_center.coordinator import (
    LiveCoordinator,
    ScheduleCoordinator,
)
from custom_components.nascar_race_center.models import ProviderError, Race, Session
from custom_components.nascar_race_center.reference import Driver, Track
from custom_components.nascar_race_center.reference_coordinator import (
    ReferenceCoordinator,
)


@pytest.fixture
async def make_schedule(hass: HomeAssistant):
    """Release all race boundary timers created outside entry setup."""
    coordinators = []

    def create(entry, provider, series):
        coordinator = ScheduleCoordinator(hass, entry, provider, series)
        coordinators.append(coordinator)
        return coordinator

    yield create
    for coordinator in coordinators:
        await coordinator.async_shutdown()


async def test_reference_outage_preserves_last_good_and_other_directory(
    hass: HomeAssistant,
) -> None:
    """A driver failure retains the selection data and refreshes valid tracks."""
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    provider = Mock()
    provider.async_get_drivers = AsyncMock(
        return_value=(Driver(101, "Fixture Driver"),)
    )
    provider.async_get_tracks = AsyncMock(return_value=(Track(201, "Fixture Track"),))
    coordinator = ReferenceCoordinator(hass, entry, provider)
    try:
        await coordinator.async_refresh()
        old_driver = coordinator.data.drivers[101]
        old_time = coordinator.data.updated_at["drivers"]
        provider.async_get_drivers.side_effect = ProviderError(
            "Driver outage", status=503
        )
        provider.async_get_tracks.return_value = (Track(201, "Renamed Track"),)
        await coordinator.async_refresh()
        assert coordinator.data.drivers[101] is old_driver
        assert coordinator.data.updated_at["drivers"] == old_time
        assert coordinator.data.tracks[201].name == "Renamed Track"
        assert coordinator.data.failed_feeds == frozenset({"drivers"})
        assert coordinator.last_error_status == {"drivers": 503}
        provider.async_get_drivers.side_effect = None
        provider.async_get_drivers.return_value = (Driver(101, "Updated Driver"),)
        await coordinator.async_refresh()
        assert not coordinator.data.failed_feeds
        assert coordinator.data.drivers[101].name == "Updated Driver"
    finally:
        await coordinator.async_shutdown()


async def test_both_reference_failures_do_not_disable_schedules(
    hass: HomeAssistant,
) -> None:
    """Directory failures remain optional even on first installation."""
    provider = Mock()
    provider.async_get_drivers = AsyncMock(side_effect=ProviderError("No drivers"))
    provider.async_get_tracks = AsyncMock(side_effect=ProviderError("No tracks"))
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoReferenceProvider",
        return_value=provider,
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.runtime_data.schedule.last_update_success
    assert entry.runtime_data.reference.data.failed_feeds == {"drivers", "tracks"}
    reference = entry.runtime_data.reference
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    provider.async_get_drivers.reset_mock()
    provider.async_get_tracks.reset_mock()
    await reference.async_request_refresh()
    async_fire_time_changed(hass, datetime.now(UTC) + timedelta(days=2))
    await hass.async_block_till_done()
    provider.async_get_drivers.assert_not_awaited()
    provider.async_get_tracks.assert_not_awaited()


async def test_upcoming_season_remains_usable_when_current_feed_missing(
    hass: HomeAssistant, make_schedule
) -> None:
    """A missing late-season feed cannot hide an already published next year."""
    now = datetime(2026, 12, 15, tzinfo=UTC)
    upcoming = Race(
        1, 77, "Upcoming season", datetime(2027, 2, 1, tzinfo=UTC), season=2027
    )
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        side_effect=[ProviderError("Current unpublished", status=404), (upcoming,)]
    )
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    coordinator = make_schedule(entry, provider, (1,))
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=now,
    ):
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        assert coordinator.next_race(1) == upcoming


async def test_observed_postponed_weekend_survives_new_year(
    hass: HomeAssistant, make_schedule
) -> None:
    """A known prior-season event remains visible until its revised times pass."""
    carried = Race(
        1,
        88,
        "Postponed fixture",
        datetime(2027, 1, 2, tzinfo=UTC),
        season=2026,
        sessions=(
            Session(
                "qualifying",
                "Qualifying",
                start_time=datetime(2027, 1, 1, tzinfo=UTC),
                end_time=datetime(2027, 1, 1, 1, tzinfo=UTC),
            ),
        ),
    )
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        side_effect=[(carried,), (), (), (carried,)]
    )
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    coordinator = make_schedule(entry, provider, (1,))
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=datetime(2026, 12, 31, tzinfo=UTC),
    ):
        await coordinator.async_refresh()
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=datetime(2027, 1, 1, tzinfo=UTC),
    ):
        await coordinator.async_refresh()
        assert coordinator.next_race(1) == carried


async def test_january_restart_discovers_only_remaining_previous_season_events(
    hass: HomeAssistant, make_schedule
) -> None:
    """Cold startup finds a cross-year event without loading past race history."""
    now = datetime(2027, 1, 1, tzinfo=UTC)
    cross_year = Race(
        1, 81, "Previous season postponed race", now + timedelta(days=2), season=2026
    )
    ongoing = Race(
        1,
        82,
        "Ongoing previous-season session",
        now - timedelta(hours=1),
        season=2026,
        sessions=(
            Session(
                "race",
                "Race",
                start_time=now - timedelta(hours=1),
                end_time=now + timedelta(hours=1),
            ),
        ),
    )
    completed = Race(
        1, 83, "Previous completed race", now - timedelta(days=4), season=2026
    )
    unknown = Race(1, 84, "Previous unknown time", season=2026)
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        side_effect=[(), (cross_year, ongoing, completed, unknown)]
    )
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    coordinator = make_schedule(entry, provider, (1,))
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=now,
    ):
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        assert coordinator.next_race(1) == cross_year
        assert {race.race_id for race in coordinator.usable_races(1)} == {81, 82}
    assert provider.async_get_schedule.call_args_list == [call(2027, 1), call(2026, 1)]


async def test_current_outage_keeps_next_season_usable_without_promoting_old_data(
    hass: HomeAssistant, make_schedule
) -> None:
    """A published next season stays usable while failed current data is retained."""
    now = datetime(2026, 11, 15, tzinfo=UTC)
    current = Race(1, 81, "Current season race", now + timedelta(hours=1), season=2026)
    upcoming = Race(
        1, 82, "Next season race", datetime(2027, 2, 1, tzinfo=UTC), season=2027
    )
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        side_effect=[
            (current,),
            (upcoming,),
            ProviderError("Current outage", status=503),
            (upcoming,),
        ]
    )
    provider.async_get_live = AsyncMock(return_value=None)
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    coordinator = make_schedule(entry, provider, (1,))
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=now,
    ):
        await coordinator.async_refresh()
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        assert current in coordinator.data.races[1]
        assert coordinator.data.failed_seasons == {1: frozenset({2026})}
        assert coordinator.usable_races(1) == (upcoming,)
        assert coordinator.next_race(1) == upcoming
        live = LiveCoordinator(hass, entry, provider, coordinator, 300)
        try:
            await live.async_refresh()
            assert live.update_interval >= timedelta(hours=6)
        finally:
            await live.async_shutdown()


async def test_current_outage_and_empty_next_season_cannot_claim_success(
    hass: HomeAssistant, make_schedule
) -> None:
    """An empty optional feed cannot overwrite valid last-good current schedules."""
    now = datetime(2026, 11, 15, tzinfo=UTC)
    current = Race(1, 81, "Current race", now + timedelta(days=1), season=2026)
    upcoming = Race(1, 82, "Next race", datetime(2027, 2, 1, tzinfo=UTC), season=2027)
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        side_effect=[
            (current,),
            (upcoming,),
            ProviderError("Current outage", status=503),
            (),
        ]
    )
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    coordinator = make_schedule(entry, provider, (1,))
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=now,
    ):
        await coordinator.async_refresh()
        previous = coordinator.data
        await coordinator.async_refresh()
        assert not coordinator.last_update_success
        assert coordinator.data is previous
        assert current in coordinator.data.races[1]
        assert coordinator.usable_races(1) == ()
        assert coordinator.next_race(1) is None


async def test_next_season_failure_keeps_current_available_and_future_cache_unavailable(
    hass: HomeAssistant, make_schedule
) -> None:
    """Current data stays current without selecting a retained failed next season."""
    now = datetime(2026, 11, 15, tzinfo=UTC)
    current = Race(
        1, 81, "Completed current race", now - timedelta(days=1), season=2026
    )
    upcoming = Race(1, 82, "Next race", datetime(2027, 2, 1, tzinfo=UTC), season=2027)
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        side_effect=[
            (current,),
            (upcoming,),
            (current,),
            ProviderError("Next outage", status=503),
        ]
    )
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    coordinator = make_schedule(entry, provider, (1,))
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=now,
    ):
        await coordinator.async_refresh()
        await coordinator.async_refresh()
        assert coordinator.last_update_success
        assert upcoming in coordinator.data.races[1]
        assert coordinator.data.failed_seasons == {1: frozenset({2027})}
        assert coordinator.usable_races(1) == (current,)
        assert coordinator.next_race(1) is None


async def test_extreme_race_time_does_not_overflow_boundary_timer(
    hass: HomeAssistant, make_schedule
) -> None:
    """A representable source time need not support the extra timer offset."""
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        return_value=(Race(1, 81, "Extreme time", datetime.max.replace(tzinfo=UTC)),)
    )
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    coordinator = make_schedule(entry, provider, (1,))
    await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert coordinator._unsub_boundary is None
