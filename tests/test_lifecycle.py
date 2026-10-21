"""Exercise entry-owned timers through real HA unload and setup lifecycles."""

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed
from test_init import demo_entry

from custom_components.nascar_race_center import RuntimeData, async_unload_entry
from custom_components.nascar_race_center.models import LiveSnapshot, Race


def timed_provider() -> Mock:
    """Arm both custom timers, before any normal provider poll is due."""
    now = dt_util.utcnow()
    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        return_value=(Race(1, 1, "Synthetic race", now + timedelta(minutes=1)),)
    )
    provider.async_get_live = AsyncMock(
        return_value=LiveSnapshot(1, 1, lap=0, source_updated_at=now)
    )
    return provider


async def assert_quiet(hass: HomeAssistant, runtime: RuntimeData) -> None:
    """Old coordinators cannot notify entities, poll, or re-arm local timers."""
    schedule, live, reference = runtime.schedule, runtime.live, runtime.reference
    assert schedule._unsub_boundary is None
    assert live._unsub_source_expiry is None
    with (
        patch.object(schedule, "async_update_listeners") as schedule_update,
        patch.object(live, "async_update_listeners") as live_update,
        patch.object(reference, "async_update_listeners") as reference_update,
        patch.object(reference.provider, "async_get_drivers") as get_drivers,
        patch.object(reference.provider, "async_get_tracks") as get_tracks,
    ):
        # Also exercise queued refresh requests after shutdown.
        await schedule.async_request_refresh()
        await live.async_request_refresh()
        await reference.async_request_refresh()
        future = dt_util.utcnow() + timedelta(hours=7)
        with patch(
            "custom_components.nascar_race_center.coordinator.dt_util.utcnow",
            return_value=future,
        ):
            async_fire_time_changed(hass, future)
            await hass.async_block_till_done()
        schedule_update.assert_not_called()
        live_update.assert_not_called()
        reference_update.assert_not_called()
        get_drivers.assert_not_called()
        get_tracks.assert_not_called()
    assert schedule._unsub_boundary is None
    assert live._unsub_source_expiry is None


@pytest.mark.parametrize("reload", [False, True])
async def test_entry_unload_and_reload_cancel_both_timers(
    hass: HomeAssistant, reload: bool
) -> None:
    """Only a replacement entry may keep timers and polling after reload."""
    provider = timed_provider()
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        old = entry.runtime_data
        assert old.schedule._unsub_boundary is not None
        assert old.live._unsub_source_expiry is not None
        if reload:
            assert await hass.config_entries.async_reload(entry.entry_id)
            await hass.async_block_till_done()
            assert entry.runtime_data is not old
            assert entry.runtime_data.schedule._unsub_boundary is not None
            assert entry.runtime_data.live._unsub_source_expiry is not None
            replacement = entry.runtime_data
            # Unload the replacement before advancing time beyond poll deadlines.
            assert await hass.config_entries.async_unload(entry.entry_id)
        else:
            assert await hass.config_entries.async_unload(entry.entry_id)
        await hass.async_block_till_done()
        provider.async_get_schedule.reset_mock()
        provider.async_get_live.reset_mock()
        await assert_quiet(hass, old)
        if reload:
            await assert_quiet(hass, replacement)
        provider.async_get_schedule.assert_not_awaited()
        provider.async_get_live.assert_not_awaited()


@pytest.mark.parametrize("cancelled", [False, True])
async def test_failed_setup_cancels_both_armed_timers(
    hass: HomeAssistant, cancelled: bool
) -> None:
    """Failure/cancellation after initial refresh leaves no local callbacks."""
    provider = timed_provider()
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    error = asyncio.CancelledError() if cancelled else RuntimeError("Forwarding failed")
    with (
        patch(
            "custom_components.nascar_race_center.DemoProvider", return_value=provider
        ),
        patch.object(
            hass.config_entries, "async_forward_entry_setups", side_effect=error
        ),
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.SETUP_ERROR
    provider.async_get_schedule.reset_mock()
    provider.async_get_live.reset_mock()
    await assert_quiet(hass, entry.runtime_data)
    provider.async_get_schedule.assert_not_awaited()
    provider.async_get_live.assert_not_awaited()


@pytest.mark.parametrize("kind", ["schedule", "live", "reference"])
async def test_inflight_refresh_cannot_rearm_timer_after_unload(
    hass: HomeAssistant, kind: str
) -> None:
    """A provider result arriving after shutdown must not retain the old entry."""
    provider = timed_provider()
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    runtime = entry.runtime_data
    started, release = asyncio.Event(), asyncio.Event()
    if kind == "reference":
        method = AsyncMock(return_value=())
        runtime.reference.provider.async_get_drivers = method
    else:
        method = (
            provider.async_get_schedule
            if kind == "schedule"
            else provider.async_get_live
        )
    result = method.return_value

    async def blocked(*args: object) -> object:
        started.set()
        await release.wait()
        return result

    method.side_effect = blocked
    coordinator = getattr(runtime, kind)
    task = asyncio.create_task(coordinator.async_refresh())
    try:
        await started.wait()
        assert await hass.config_entries.async_unload(entry.entry_id)
    finally:
        release.set()
        await task
    await hass.async_block_till_done()
    await assert_quiet(hass, runtime)


async def test_failed_platform_unload_keeps_loaded_entry_timers(
    hass: HomeAssistant,
) -> None:
    """Do not disable the still-loaded integration if a platform refuses unload."""
    provider = timed_provider()
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    runtime = entry.runtime_data
    with patch.object(
        hass.config_entries, "async_unload_platforms", return_value=False
    ):
        assert not await async_unload_entry(hass, entry)
    assert runtime.schedule._unsub_boundary is not None
    assert runtime.live._unsub_source_expiry is not None
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    await assert_quiet(hass, runtime)
