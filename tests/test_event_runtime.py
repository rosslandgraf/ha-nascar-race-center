"""Real HA lifecycle, storage ordering, options and single-source event tests."""

import asyncio
from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import async_fire_time_changed
from test_events import BASE, sample
from test_init import demo_entry

from custom_components.nascar_race_center.events import (
    EVENT_NAMESPACE,
    FAVORITE_EVENTS,
    GENERAL_EVENTS,
    EventType,
)
from custom_components.nascar_race_center.models import Race


def event_options(enabled=True):
    return {
        "racing_events": enabled,
        "event_types": [kind.value for kind in GENERAL_EVENTS],
        "favorite_event_types": [kind.value for kind in FAVORITE_EVENTS],
        "favorite_drivers": ["99001"],
    }


def provider_mock():
    provider = Mock()
    provider.async_get_live = AsyncMock(return_value=sample(0))
    provider.async_get_schedule = AsyncMock(return_value=())
    return provider


async def update(hass, freezer, runtime, second, **changes):
    freezer.move_to(BASE + timedelta(seconds=second))
    runtime.live.async_set_updated_data(sample(second, **changes))
    await hass.async_block_till_done()


@pytest.mark.parametrize("series", [["1"], ["1", "2", "3"]])
async def test_one_observation_one_global_event_and_silent_reload(
    hass, freezer, series
):
    freezer.move_to(BASE)
    provider = provider_mock()
    entry = demo_entry(series)
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=event_options())
    seen = []
    hass.bus.async_listen(EVENT_NAMESPACE, lambda event: seen.append(event.data))
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        runtime = entry.runtime_data
        assert runtime.events.status == "ready"
        assert seen == []
        await update(hass, freezer, runtime, 30, flag="yellow")
        assert [event["event_type"] for event in seen] == [EventType.FLAG]
        assert seen[0]["source"] == "demo"
        stored = await runtime.events.store.async_load()
        assert seen[0]["event_id"] in stored["ids"]
        for _ in range(5):
            runtime.live.async_update_listeners()
        await hass.async_block_till_done()
        assert len(seen) == 1
        provider.async_get_live.return_value = sample(60, flag="red", position=1)
        freezer.move_to(BASE + timedelta(seconds=60))
        assert await hass.config_entries.async_reload(entry.entry_id)
        await hass.async_block_till_done()
        assert len(seen) == 1
        assert runtime.events._task is None
        assert runtime.events._unsubs == []
        assert runtime.events._timer is None
        await update(hass, freezer, entry.runtime_data, 90, flag="red", position=1)
        assert len(seen) == 1
        assert await hass.config_entries.async_unload(entry.entry_id)
        runtime.live.async_set_updated_data(sample(120, flag="green"))
        await hass.async_block_till_done()
        assert len(seen) == 1
        # Neither events nor favorites add provider requests of their own.
        assert provider.async_get_live.await_count == 2


async def test_legacy_default_disabled_has_no_storage_or_event_work(hass, freezer):
    freezer.move_to(BASE)
    entry = demo_entry()
    entry.add_to_hass(hass)
    seen = []
    hass.bus.async_listen(EVENT_NAMESPACE, lambda event: seen.append(event.data))
    with patch(
        "custom_components.nascar_race_center.DemoProvider",
        return_value=provider_mock(),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        runtime = entry.runtime_data
        assert runtime.events.status == "disabled"
        assert runtime.events._unsubs == []
        with patch.object(runtime.events.store, "async_save") as save:
            await update(hass, freezer, runtime, 30, flag="yellow", position=1)
            save.assert_not_called()
        assert seen == []
        assert await hass.config_entries.async_unload(entry.entry_id)


async def test_source_outage_stale_unselected_series_and_reconnect(hass, freezer):
    freezer.move_to(BASE)
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=event_options())
    seen = []
    hass.bus.async_listen(EVENT_NAMESPACE, lambda event: seen.append(event.data))
    with patch(
        "custom_components.nascar_race_center.DemoProvider",
        return_value=provider_mock(),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        runtime = entry.runtime_data
        runtime.live.async_set_update_error(UpdateFailed("synthetic outage"))
        await hass.async_block_till_done()
        await update(hass, freezer, runtime, 30, flag="yellow", position=1)
        await update(hass, freezer, runtime, 60, series_id=2, flag="red")
        await update(hass, freezer, runtime, 90, flag="red")
        assert seen == []
        # Local stale callbacks break continuity without any provider call.
        freezer.move_to(BASE + timedelta(minutes=20))
        runtime.live.async_update_listeners()
        await hass.async_block_till_done()
        await update(hass, freezer, runtime, 1230, flag="green", position=1)
        assert seen == []
        assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize(
    "error", [OSError("disk unavailable"), ValueError("serialization")]
)
async def test_storage_failure_prevents_publication_and_preserves_entities(
    hass, freezer, error
):
    freezer.move_to(BASE)
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=event_options())
    seen = []
    hass.bus.async_listen(EVENT_NAMESPACE, lambda event: seen.append(event.data))
    with patch(
        "custom_components.nascar_race_center.DemoProvider",
        return_value=provider_mock(),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        runtime = entry.runtime_data
        with patch.object(runtime.events.store, "async_save", side_effect=error):
            await update(hass, freezer, runtime, 30, flag="yellow")
        assert runtime.events.status == "ledger_error"
        assert seen == []
        assert runtime.live.last_update_success
        assert runtime.events._unsubs == []
        assert await hass.config_entries.async_unload(entry.entry_id)


async def test_invalid_ledger_leaves_events_disabled_but_setup_usable(hass, freezer):
    freezer.move_to(BASE)
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=event_options())
    with (
        patch(
            "custom_components.nascar_race_center.DemoProvider",
            return_value=provider_mock(),
        ),
        patch(
            "custom_components.nascar_race_center.event_runtime.Store.async_load",
            return_value={"schema": 42},
        ),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        runtime = entry.runtime_data
        assert runtime.events.status == "ledger_error"
        assert runtime.events._unsubs == []
        assert runtime.events._timer is None
        assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize(
    "stop", ["unload", "outage", "switch", "switch_return", "future", "unknown_flag"]
)
async def test_inflight_disk_write_cannot_publish_after_evidence_is_lost(
    hass, freezer, stop
):
    freezer.move_to(BASE)
    entry = demo_entry(["1", "2"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=event_options())
    seen = []
    hass.bus.async_listen(EVENT_NAMESPACE, lambda event: seen.append(event.data))
    with patch(
        "custom_components.nascar_race_center.DemoProvider",
        return_value=provider_mock(),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        runtime = entry.runtime_data
        entered, release = asyncio.Event(), asyncio.Event()
        original_save = runtime.events.store.async_save

        async def slow_save(data):
            entered.set()
            await release.wait()
            await original_save(data)

        with patch.object(runtime.events.store, "async_save", side_effect=slow_save):
            freezer.move_to(BASE + timedelta(seconds=30))
            runtime.live.async_set_updated_data(sample(30, flag="yellow"))
            await asyncio.wait_for(entered.wait(), timeout=1)
            if stop == "unload":
                unload = hass.async_create_task(
                    hass.config_entries.async_unload(entry.entry_id), eager_start=False
                )
                for _ in range(100):
                    if runtime.events._stopped:
                        break
                    await asyncio.sleep(0)
                assert runtime.events._stopped
                release.set()
                assert await unload
            elif stop == "outage":
                runtime.live.async_set_update_error(UpdateFailed("synthetic outage"))
            elif stop == "future":
                runtime.live.async_set_updated_data(sample(300, flag="red"))
            elif stop == "unknown_flag":
                runtime.live.async_set_updated_data(sample(30, flag=None))
            else:
                runtime.live.async_set_updated_data(sample(30, series_id=2, flag="red"))
                if stop == "switch_return":
                    runtime.live.async_set_updated_data(sample(30, flag="yellow"))
            release.set()
            await hass.async_block_till_done()
        assert seen == []
        if stop != "unload":
            assert await hass.config_entries.async_unload(entry.entry_id)
        assert runtime.events._task is None


async def test_reminder_timer_is_local_once_and_cancelled_on_unload(hass, freezer):
    freezer.move_to(BASE)
    provider = provider_mock()
    # Keep the reminder before ordinary polling and expiry deadlines.
    provider.async_get_schedule.return_value = (
        Race(1, 9001, "Fictional", BASE + timedelta(minutes=31)),
    )
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=event_options())
    seen = []
    hass.bus.async_listen(EVENT_NAMESPACE, lambda event: seen.append(event.data))
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        runtime = entry.runtime_data
        assert runtime.events._timer is not None
        calls = provider.async_get_schedule.await_count
        freezer.move_to(BASE + timedelta(minutes=1))
        async_fire_time_changed(hass, BASE + timedelta(minutes=1))
        await hass.async_block_till_done()
        assert [event["event_type"] for event in seen] == [EventType.UPCOMING]
        assert seen[0]["run_id"] is None
        assert provider.async_get_schedule.await_count == calls
        runtime.schedule.async_update_listeners()
        await hass.async_block_till_done()
        assert len(seen) == 1
        assert await hass.config_entries.async_unload(entry.entry_id)
        assert runtime.events._timer is None


async def test_option_changes_rebaseline_and_queue_remains_bounded(hass, freezer):
    freezer.move_to(BASE)
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=event_options())
    seen = []
    hass.bus.async_listen(EVENT_NAMESPACE, lambda event: seen.append(event.data))
    with patch(
        "custom_components.nascar_race_center.DemoProvider",
        return_value=provider_mock(),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        old = entry.runtime_data
        hass.config_entries.async_update_entry(
            entry, options={**event_options(), "event_top_n": 20}
        )
        await hass.async_block_till_done()
        assert entry.runtime_data is not old
        assert seen == []
        runtime = entry.runtime_data
        # A burst stays bounded and establishes a new baseline at overflow.
        for second in range(1, 42):
            freezer.move_to(BASE + timedelta(seconds=second))
            runtime.live.async_set_updated_data(sample(second, flag="green"))
            assert len(runtime.events._queue) <= 32
        await hass.async_block_till_done()
        assert seen == []
        await update(hass, freezer, runtime, 60, flag="yellow")
        assert [event["event_type"] for event in seen] == [EventType.FLAG]
        assert await hass.config_entries.async_unload(entry.entry_id)


async def test_renamed_corrupt_ledger_stays_disabled_across_reload(hass, freezer):
    freezer.move_to(BASE)
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=event_options())
    with (
        patch(
            "custom_components.nascar_race_center.DemoProvider",
            return_value=provider_mock(),
        ),
        patch(
            "custom_components.nascar_race_center.event_runtime.EventRuntime._ledger_exists",
            return_value=True,
        ),
        patch(
            "custom_components.nascar_race_center.event_runtime.Store.async_load",
            return_value=None,
        ),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        assert entry.runtime_data.events.status == "ledger_error"
        assert await hass.config_entries.async_reload(entry.entry_id)
        assert entry.runtime_data.events.status == "ledger_error"
        assert await hass.config_entries.async_unload(entry.entry_id)


async def test_store_swallowed_write_failure_is_detected_by_readback(hass, freezer):
    freezer.move_to(BASE)
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(entry, options=event_options())
    seen = []
    hass.bus.async_listen(EVENT_NAMESPACE, lambda event: seen.append(event.data))
    with patch(
        "custom_components.nascar_race_center.DemoProvider",
        return_value=provider_mock(),
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        runtime = entry.runtime_data
        # Reproduce the public Store contract: log/return without persisting.
        with patch.object(runtime.events.store, "async_save", return_value=None):
            await update(hass, freezer, runtime, 30, flag="yellow")
        assert runtime.events.status == "ledger_error"
        assert seen == []
        assert await hass.config_entries.async_unload(entry.entry_id)
