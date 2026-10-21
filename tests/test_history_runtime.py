"""Actual Home Assistant setup, history request budgets and lifecycle cleanup."""

import asyncio
import json
from datetime import timedelta
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import async_fire_time_changed
from test_history import KEY, fixture
from test_init import demo_entry
from test_phase3b_setup import cf_entry
from test_scoring import NOW

from custom_components.nascar_race_center import api
from custom_components.nascar_race_center.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.nascar_race_center.endpoints import (
    BASE_URL,
    historical_path,
    is_historical_path,
)
from custom_components.nascar_race_center.history_models import (
    HistoryDataset as Kind,
)
from custom_components.nascar_race_center.history_models import (
    HistoryStatus as Status,
)
from custom_components.nascar_race_center.history_provider import DemoHistoryProvider


@pytest.fixture
def mock_recorder_before_hass(request):
    if "recorder_mock" in request.fixturenames:
        request.getfixturevalue("recorder_db_url")


async def test_actual_cf_startup_refresh_demand_and_reload_budget(
    hass, aioclient_mock, freezer, monkeypatch
):
    freezer.move_to(NOW)
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    entry = await cf_entry(hass, aioclient_mock)
    assert aioclient_mock.call_count == 7
    runtime = entry.runtime_data
    before_entities = {
        e.unique_id
        for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    }
    await runtime.live.async_refresh()
    await runtime.schedule.async_refresh()
    await runtime.reference.async_refresh()
    await runtime.scoring.async_refresh()
    assert aioclient_mock.call_count == 7
    assert not runtime.provider.api._history_cache
    aioclient_mock.get(
        BASE_URL + historical_path(KEY, Kind.LAPS), json=fixture(Kind.LAPS)
    )
    responses = await asyncio.gather(
        *(runtime.history.async_get(KEY, (Kind.LAPS,)) for _ in range(20))
    )
    assert all(r.status == Status.AVAILABLE for r in responses)
    assert aioclient_mock.call_count == 8
    await runtime.history.async_get(KEY, (Kind.LAPS,))
    assert aioclient_mock.call_count == 8
    assert len(runtime.provider.api._history_cache) == 1
    assert runtime.live.data.race_id != KEY.race_id
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert "Fictional Archive Driver" not in json.dumps(diagnostics)
    assert "LapTime" not in json.dumps(diagnostics)
    assert {
        e.unique_id
        for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    } == before_entities
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert runtime.history.closed
    assert not runtime.provider.api._history_cache
    assert aioclient_mock.call_count == 8
    replacement = entry.runtime_data
    assert replacement.history is not runtime.history
    assert not replacement.history.closed
    assert not async_get_clientsession(hass).closed
    assert await hass.config_entries.async_unload(entry.entry_id)
    clock[0] += 40000
    freezer.tick(timedelta(hours=10))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert replacement.history.closed
    assert aioclient_mock.call_count == 8


@pytest.mark.parametrize("shutdown", ["unload", "reload", "stop"])
async def test_inflight_history_is_cancelled_by_real_ha_lifecycle(hass, shutdown):
    entry = demo_entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    history = entry.runtime_data.history
    started, cancelled = asyncio.Event(), asyncio.Event()

    async def blocked(*_):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    history.provider.async_get_history = AsyncMock(side_effect=blocked)
    consumer = asyncio.create_task(history.async_get(KEY, (Kind.LAPS,)))
    await started.wait()
    if shutdown == "unload":
        assert await hass.config_entries.async_unload(entry.entry_id)
    elif shutdown == "reload":
        assert await hass.config_entries.async_reload(entry.entry_id)
    else:
        hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
        await hass.async_block_till_done()
    with pytest.raises(asyncio.CancelledError):
        await consumer
    assert cancelled.is_set()
    assert history.closed
    assert not history._flights
    if shutdown == "reload":
        assert not entry.runtime_data.history.closed
        assert await hass.config_entries.async_unload(entry.entry_id)


async def test_restart_recreates_empty_history_cache_without_restoring_raw_data(
    hass, aioclient_mock, freezer
):
    freezer.move_to(NOW)
    entry = await cf_entry(hass, aioclient_mock)
    aioclient_mock.get(
        BASE_URL + historical_path(KEY, Kind.LAPS), json=fixture(Kind.LAPS)
    )
    await entry.runtime_data.history.async_get(KEY, (Kind.LAPS,))
    old_provider = entry.runtime_data.provider
    assert await hass.config_entries.async_unload(entry.entry_id)
    # Model loss of all process-memory providers, retaining only HA's Store.
    hass.data["nascar_race_center"].pop(entry.entry_id)
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert entry.runtime_data.provider is not old_provider
    assert not entry.runtime_data.provider.api._history_cache
    history_urls = [
        call[1]
        for call in aioclient_mock.mock_calls
        if is_historical_path(call[1].path)
    ]
    assert len(history_urls) == 1
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize("cancel", [False, True])
async def test_failed_or_cancelled_setup_closes_history(hass, cancel):
    entry = demo_entry()
    entry.add_to_hass(hass)
    started = asyncio.Event()

    async def forward(*_):
        started.set()
        if cancel:
            await asyncio.Event().wait()
        raise RuntimeError("Fictional setup failure")

    with patch.object(
        hass.config_entries, "async_forward_entry_setups", side_effect=forward
    ):
        setup = asyncio.create_task(hass.config_entries.async_setup(entry.entry_id))
        await started.wait()
        if cancel:
            setup.cancel()
            with pytest.raises(asyncio.CancelledError):
                await setup
        else:
            assert not await setup
        assert entry.runtime_data.history.closed


async def test_offline_history_does_not_perform_network_work(hass, aioclient_mock):
    entry = demo_entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    response = await entry.runtime_data.history.async_get(KEY, tuple(Kind))
    assert response.status == Status.AVAILABLE
    assert isinstance(entry.runtime_data.history.provider, DemoHistoryProvider)
    assert aioclient_mock.call_count == 0
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_history_reads_add_zero_recorder_rows(recorder_mock, hass):
    from homeassistant.components.recorder.db_schema import States
    from pytest_homeassistant_custom_component.components.recorder.common import (
        async_wait_recording_done,
    )
    from sqlalchemy import func, select

    entry = demo_entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()

    def count():
        with recorder_mock.get_session() as session:
            return session.scalar(select(func.count(States.state_id)))

    await async_wait_recording_done(hass)
    before = await hass.async_add_executor_job(count)
    assert before > 0
    for _ in range(10):
        response = await entry.runtime_data.history.async_get(KEY, tuple(Kind))
        assert response.status == Status.AVAILABLE
    await async_wait_recording_done(hass)
    assert await hass.async_add_executor_job(count) == before
    assert await hass.config_entries.async_unload(entry.entry_id)
