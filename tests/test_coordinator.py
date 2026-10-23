"""Verify scheduling, partial outages, and source freshness with normalized data."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nascar_race_center.api import ProviderError
from custom_components.nascar_race_center.const import DOMAIN
from custom_components.nascar_race_center.coordinator import (
    LiveCoordinator,
    ScheduleCoordinator,
)
from custom_components.nascar_race_center.models import LiveSnapshot, Race

NOW = datetime(2026, 10, 20, 12, tzinfo=UTC)


def provider_mock() -> Mock:
    """Provide only async provider methods so no real HTTP can occur."""
    provider = Mock()
    provider.async_get_schedule = AsyncMock(return_value=())
    provider.async_get_live = AsyncMock(return_value=None)
    return provider


def entry_for(hass: HomeAssistant) -> MockConfigEntry:
    """Register an entry that owns coordinator background tasks."""
    entry = MockConfigEntry(domain=DOMAIN)
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def make_schedule(hass: HomeAssistant):
    """Own timers created by unit-test coordinators outside entry setup."""
    coordinators = []

    def create(entry, provider, series):
        coordinator = ScheduleCoordinator(hass, entry, provider, series)
        coordinators.append(coordinator)
        return coordinator

    yield create
    for coordinator in coordinators:
        await coordinator.async_shutdown()


@pytest.fixture
async def make_live(hass: HomeAssistant):
    """Own expiry timers for live coordinators tested outside entry setup."""
    coordinators = []

    def create(entry, provider, schedule, interval):
        coordinator = LiveCoordinator(hass, entry, provider, schedule, interval)
        coordinators.append(coordinator)
        return coordinator

    yield create
    for coordinator in coordinators:
        await coordinator.async_shutdown()


async def test_next_race_handles_unsorted_and_rescheduled_races(
    hass: HomeAssistant,
    make_schedule,
) -> None:
    """A revised start time replaces the old next race on the next refresh."""
    provider = provider_mock()
    first = Race(1, 10, "Synthetic first race", NOW + timedelta(days=1))
    second = Race(1, 11, "Synthetic second race", NOW + timedelta(days=2))
    unknown = Race(1, 12, "Unannounced start")
    past = Race(1, 9, "Completed race", NOW - timedelta(days=1))
    provider.async_get_schedule.return_value = (unknown, second, past, first)
    coordinator = make_schedule(entry_for(hass), provider, (1,))
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=NOW,
    ):
        await coordinator.async_refresh()
        assert coordinator.next_race(1) == first
        postponed = Race(1, 10, first.name, NOW + timedelta(days=3))
        provider.async_get_schedule.return_value = (postponed, second, unknown)
        await coordinator.async_refresh()
        assert coordinator.next_race(1) == second


async def test_no_scheduled_race_is_empty_success(
    hass: HomeAssistant, make_schedule
) -> None:
    """An off-season empty schedule is distinct from a failed request."""
    coordinator = make_schedule(entry_for(hass), provider_mock(), (1,))
    await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert coordinator.data.races == {1: ()}
    assert coordinator.data.failed_series == frozenset()
    assert coordinator.next_race(1) is None


async def test_partial_series_failure_retains_other_schedules(
    hass: HomeAssistant,
    make_schedule,
) -> None:
    """An optional or unavailable series never discards another valid schedule."""
    provider = provider_mock()
    cup = Race(1, 10, "Cup fixture", NOW + timedelta(days=1))
    trucks = Race(3, 30, "Truck fixture", NOW + timedelta(days=1))
    provider.async_get_schedule.side_effect = [(cup,), (trucks,)]
    coordinator = make_schedule(entry_for(hass), provider, (1, 3))
    await coordinator.async_refresh()
    provider.async_get_schedule.side_effect = [ProviderError("Missing feed"), (trucks,)]
    await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert coordinator.data.failed_series == frozenset({1})
    assert coordinator.data.races[1] == (cup,)
    assert coordinator.data.races[3] == (trucks,)


async def test_total_failure_retains_last_successful_data(
    hass: HomeAssistant, make_schedule
) -> None:
    """Coordinator state marks an outage while preserving data for diagnostics."""
    provider = provider_mock()
    race = Race(1, 10, "Fixture race", NOW + timedelta(days=1))
    provider.async_get_schedule.return_value = (race,)
    coordinator = make_schedule(entry_for(hass), provider, (1,))
    await coordinator.async_refresh()
    previous = coordinator.data
    provider.async_get_schedule.side_effect = ProviderError("Denied", status=403)
    await coordinator.async_refresh()
    assert not coordinator.last_update_success
    assert coordinator.data is previous
    assert coordinator.last_error_status == 403


async def test_upcoming_season_is_optional_in_november(
    hass: HomeAssistant, make_schedule
) -> None:
    """Unpublished next-year data must not prevent current-year schedules."""
    provider = provider_mock()
    now = datetime(2026, 11, 1, 12, tzinfo=UTC)
    race = Race(1, 10, "Season finale", now + timedelta(days=1))
    provider.async_get_schedule.side_effect = [
        (race,),
        ProviderError("Next season unpublished", status=404),
    ]
    coordinator = make_schedule(entry_for(hass), provider, (1,))
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=now,
    ):
        await coordinator.async_refresh()
    assert coordinator.last_update_success
    assert coordinator.data.races[1] == (race,)
    assert provider.async_get_schedule.call_args_list == [call(2026, 1), call(2027, 1)]


async def test_year_rollover_routes_new_season(
    hass: HomeAssistant, make_schedule
) -> None:
    """An existing entry requests the new year without reconfiguration."""
    provider = provider_mock()
    coordinator = make_schedule(entry_for(hass), provider, (2,))
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=datetime(2026, 12, 31, 23, tzinfo=UTC),
    ):
        await coordinator.async_refresh()
    provider.async_get_schedule.reset_mock()
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=datetime(2027, 1, 1, 1, tzinfo=UTC),
    ):
        await coordinator.async_refresh()
    assert provider.async_get_schedule.call_args_list == [
        call(2027, 2),
        call(2026, 2),
    ]


async def test_live_outage_does_not_fail_schedule(
    hass: HomeAssistant, make_schedule, make_live
) -> None:
    """Live endpoint failure is independent of the core schedule coordinator."""
    provider = provider_mock()
    entry = entry_for(hass)
    schedule = make_schedule(entry, provider, (1,))
    await schedule.async_refresh()
    provider.async_get_live.side_effect = ProviderError(
        "Rate limited", status=429, retry_after=7200
    )
    live = make_live(entry, provider, schedule, 300)
    await live.async_refresh()
    assert schedule.last_update_success
    assert not live.last_update_success
    assert live.last_error_status == 429
    assert live.last_successful_update is None
    assert live.update_interval >= timedelta(seconds=7200)


async def test_old_live_response_does_not_trigger_active_polling(
    hass: HomeAssistant,
    make_schedule,
    make_live,
) -> None:
    """A freshly fetched archived race must not be treated as live activity."""
    provider = provider_mock()
    entry = entry_for(hass)
    schedule = make_schedule(entry, provider, (1,))
    provider.async_get_live.return_value = LiveSnapshot(
        1,
        10,
        flag="green",
        lap=10,
        source_updated_at=NOW - timedelta(days=1),
    )
    live = make_live(entry, provider, schedule, 300)
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=NOW,
    ):
        await schedule.async_refresh()
        await live.async_refresh()
        assert live.source_is_stale is True
        assert live.update_interval >= timedelta(hours=6)


async def test_live_feed_for_other_series_does_not_raise_polling_rate(
    hass: HomeAssistant,
    make_schedule,
    make_live,
) -> None:
    """The global feed cannot claim active timing for a different selected series."""
    provider = provider_mock()
    entry = entry_for(hass)
    schedule = make_schedule(entry, provider, (3,))
    provider.async_get_live.return_value = LiveSnapshot(
        1, 10, flag="green", lap=10, source_updated_at=NOW
    )
    live = make_live(entry, provider, schedule, 300)
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=NOW,
    ):
        await schedule.async_refresh()
        await live.async_refresh()
        assert live.source_is_stale is False
        assert live.update_interval >= timedelta(hours=6)


async def test_polling_uses_nearest_session_across_all_selected_series(
    hass: HomeAssistant,
    make_schedule,
    make_live,
) -> None:
    """A later series race window must win over an earlier iterated schedule."""
    provider = provider_mock()
    provider.async_get_schedule.side_effect = [
        (Race(1, 10, "Tomorrow's Cup fixture", NOW + timedelta(days=1)),),
        (Race(3, 30, "Truck fixture starting now", NOW),),
    ]
    entry = entry_for(hass)
    schedule = make_schedule(entry, provider, (1, 3))
    live = make_live(entry, provider, schedule, 300)
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=NOW,
    ):
        await schedule.async_refresh()
        await live.async_refresh()
    assert live.update_interval == timedelta(minutes=5)


async def test_future_source_clock_is_unknown_not_confirmed_live(
    hass: HomeAssistant, make_schedule, make_live
) -> None:
    """An implausible provider clock must not establish source freshness."""
    provider = provider_mock()
    entry = entry_for(hass)
    schedule = make_schedule(entry, provider, (1,))
    provider.async_get_live.return_value = LiveSnapshot(
        1,
        10,
        flag="green",
        lap=10,
        source_updated_at=NOW + timedelta(days=1),
    )
    live = make_live(entry, provider, schedule, 300)
    with patch(
        "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
        return_value=NOW,
    ):
        await schedule.async_refresh()
        await live.async_refresh()
        assert live.source_is_stale is None
        assert live.update_interval >= timedelta(hours=6)
