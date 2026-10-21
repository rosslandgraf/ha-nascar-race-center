"""Actual HA consumer API, intercepted HTTP budgets, executor and lifecycle."""

import asyncio
import threading
from dataclasses import replace
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from test_analytics import query
from test_history import KEY, fixture
from test_init import demo_entry
from test_phase3b_setup import cf_entry
from test_scoring import NOW

from custom_components.nascar_race_center import analytics_runtime
from custom_components.nascar_race_center.analytics import analyze_history
from custom_components.nascar_race_center.analytics_models import AnalyticsStatus
from custom_components.nascar_race_center.endpoints import BASE_URL, historical_path
from custom_components.nascar_race_center.history_models import HistoryDataset as Kind


@pytest.fixture
def mock_recorder_before_hass(request):
    if "recorder_mock" in request.fixturenames:
        request.getfixturevalue("recorder_db_url")


async def setup_demo(hass):
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    return entry


async def test_real_cf_interface_retains_startup_periodic_cache_and_get_budgets(
    hass, aioclient_mock, freezer, monkeypatch
):
    freezer.move_to(NOW)
    entry = await cf_entry(hass, aioclient_mock)
    runtime = entry.runtime_data
    assert aioclient_mock.call_count == 7
    ids = {
        e.unique_id
        for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    }
    await runtime.live.async_refresh()
    await runtime.schedule.async_refresh()
    await runtime.reference.async_refresh()
    await runtime.scoring.async_refresh()
    assert aioclient_mock.call_count == 7
    aioclient_mock.get(
        BASE_URL + historical_path(KEY, Kind.LAPS), json=fixture(Kind.LAPS)
    )
    thread_ids = []

    def calculate(*args):
        thread_ids.append(threading.get_ident())
        return analyze_history(*args)

    monkeypatch.setattr(analytics_runtime, "analyze_history", calculate)
    selection = query((99002,))
    results = await asyncio.gather(
        *(runtime.analytics.async_get(selection, (Kind.LAPS,)) for _ in range(20))
    )
    assert all(r is results[0] for r in results)
    assert aioclient_mock.call_count == 8
    assert len(thread_ids) == 1
    assert thread_ids[0] != threading.get_ident()
    await runtime.analytics.async_get(selection, (Kind.LAPS,))
    assert aioclient_mock.call_count == 8
    assert (
        len(thread_ids) == 2
    )  # Recalculate from existing HTTP cache; no result cache.
    assert {
        e.unique_id
        for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
    } == ids
    assert not runtime.analytics._flights
    assert await hass.config_entries.async_reload(entry.entry_id)
    assert runtime.analytics.closed and runtime.history.closed
    assert not entry.runtime_data.analytics.closed
    assert not runtime.provider.api._history_cache
    assert aioclient_mock.call_count == 8
    assert not async_get_clientsession(hass).closed
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize("shutdown", ["unload", "reload", "stop"])
async def test_actual_lifecycle_cancels_inflight_retrieval(hass, shutdown):
    entry = await setup_demo(hass)
    service = entry.runtime_data.analytics
    history = entry.runtime_data.history
    started, cancelled = asyncio.Event(), asyncio.Event()

    async def blocked(*_):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    history.provider.async_get_history = AsyncMock(side_effect=blocked)
    consumer = asyncio.create_task(service.async_get(query(), (Kind.LAPS,)))
    await started.wait()
    if shutdown == "stop":
        hass.bus.async_fire(EVENT_HOMEASSISTANT_STOP)
        await hass.async_block_till_done()
    elif shutdown == "reload":
        assert await hass.config_entries.async_reload(entry.entry_id)
    else:
        assert await hass.config_entries.async_unload(entry.entry_id)
    with pytest.raises(asyncio.CancelledError):
        await consumer
    assert service.closed and history.closed and cancelled.is_set()
    assert not service._flights
    if shutdown == "reload":
        assert await hass.config_entries.async_unload(entry.entry_id)


async def test_shared_waiter_cancellation_and_unique_computation_budget(hass):
    entry = await setup_demo(hass)
    service = entry.runtime_data.analytics
    started, release, cancelled = asyncio.Event(), asyncio.Event(), asyncio.Event()
    original = service.history.provider.async_get_history

    async def blocked(*args):
        started.set()
        try:
            await release.wait()
            return await original(*args)
        finally:
            cancelled.set()

    service.history.provider.async_get_history = AsyncMock(side_effect=blocked)
    first = asyncio.create_task(service.async_get(query(), (Kind.LAPS,)))
    second = asyncio.create_task(service.async_get(query(), (Kind.LAPS,)))
    other = asyncio.create_task(service.async_get(query(first_lap=2), (Kind.LAPS,)))
    await started.wait()
    over = await service.async_get(query(first_lap=3), (Kind.LAPS,))
    assert over.reason == "calculation_budget"
    assert service.history.provider.async_get_history.await_count == 1
    first.cancel()
    with pytest.raises(asyncio.CancelledError):
        await first
    assert not cancelled.is_set()
    release.set()
    assert (await second).status == AnalyticsStatus.UNAVAILABLE
    await other
    assert not service._flights
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_cancelled_executor_retains_slot_and_unload_drains_it(hass, monkeypatch):
    entry = await setup_demo(hass)
    service = entry.runtime_data.analytics
    started = asyncio.Event()
    release = threading.Event()
    loop = asyncio.get_running_loop()

    def blocked(*args):
        loop.call_soon_threadsafe(started.set)
        assert release.wait(timeout=10)
        return analyze_history(*args)

    monkeypatch.setattr(analytics_runtime, "analyze_history", blocked)
    consumer = asyncio.create_task(service.async_get(query(), (Kind.LAPS,)))
    await started.wait()
    consumer.cancel()
    await asyncio.sleep(0)
    assert len(service._flights) == 1
    close = asyncio.create_task(hass.config_entries.async_unload(entry.entry_id))
    await asyncio.sleep(0)
    assert not close.done()
    release.set()
    with pytest.raises(asyncio.CancelledError):
        await consumer
    assert await close
    assert service.closed and not service._flights


async def test_repeated_cancellation_keeps_worker_bounded_and_releases_slot(
    hass, monkeypatch
):
    entry = await setup_demo(hass)
    service = entry.runtime_data.analytics
    started = asyncio.Event()
    release = threading.Event()
    loop = asyncio.get_running_loop()

    def blocked(*args):
        loop.call_soon_threadsafe(started.set)
        assert release.wait(timeout=10)
        return analyze_history(*args)

    monkeypatch.setattr(analytics_runtime, "analyze_history", blocked)
    consumer = asyncio.create_task(service.async_get(query(), (Kind.LAPS,)))
    await started.wait()
    consumer.cancel()
    await asyncio.sleep(0)
    consumer.cancel()
    await asyncio.sleep(0)
    assert len(service._flights) == 1
    rejected = await service.async_get(query(), (Kind.LAPS,))
    assert rejected.reason == "calculation_draining"
    release.set()
    with pytest.raises(asyncio.CancelledError):
        await consumer
    await hass.async_block_till_done()
    assert not service._flights
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize("cancel", [False, True])
async def test_failed_or_cancelled_setup_closes_analytics(hass, cancel):
    entry = demo_entry()
    entry.add_to_hass(hass)
    started = asyncio.Event()

    async def forward(*_):
        started.set()
        if cancel:
            await asyncio.Event().wait()
        raise RuntimeError("Synthetic setup failure")

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
    assert entry.runtime_data.analytics.closed


async def test_service_validation_shutdown_before_worker_and_offline_mode(
    hass, aioclient_mock
):
    entry = await setup_demo(hass)
    service = entry.runtime_data.analytics
    assert (await service.async_get(query((99002,)), tuple(Kind))).performance[
        0
    ].result is not None
    for selection, kinds in (
        (query(), ()),
        (query(), ("laps",)),
        (query(), (Kind.LAPS, Kind.LAPS)),
        (replace(query(), key=replace(KEY, series_id=2)), (Kind.LAPS,)),
    ):
        # The demo fixture monitors series 1 only.
        with pytest.raises(ValueError):
            await service.async_get(selection, kinds)
    task = asyncio.create_task(service.async_get(query(), (Kind.LAPS,)))
    await service.async_close()
    with pytest.raises(RuntimeError):
        await task
    assert aioclient_mock.call_count == 0
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_analytics_adds_zero_recorder_rows(recorder_mock, hass):
    from homeassistant.components.recorder.db_schema import States
    from pytest_homeassistant_custom_component.components.recorder.common import (
        async_wait_recording_done,
    )
    from sqlalchemy import func, select

    entry = await setup_demo(hass)
    await hass.async_block_till_done()

    def count():
        with recorder_mock.get_session() as session:
            return session.scalar(select(func.count(States.state_id)))

    await async_wait_recording_done(hass)
    before = await hass.async_add_executor_job(count)
    assert before > 0
    for _ in range(10):
        await entry.runtime_data.analytics.async_get(query((99002,)), tuple(Kind))
    await async_wait_recording_done(hass)
    assert await hass.async_add_executor_job(count) == before
    assert await hass.config_entries.async_unload(entry.entry_id)
