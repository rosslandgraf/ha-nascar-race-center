"""Real HA entities/lifecycle with independently failing optional feed I/O."""

import asyncio
from dataclasses import replace
from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from test_phase3a_sensors import (
    entity_id,
    refresh,
    state,
)
from test_phase3a_sensors import (
    live_setup as live_setup,
)
from test_phase3a_sensors import (
    mock_recorder_before_hass as mock_recorder_before_hass,
)
from test_scoring import NOW, embedded_payload, fixture, trusted_feed

from custom_components.nascar_race_center.const import (
    CONF_DATA_USE_AUTHORIZED,
    CONF_FAVORITE_DRIVERS,
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    FAVORITE_SCORING_METRICS,
    PROVIDER_CF,
)
from custom_components.nascar_race_center.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.nascar_race_center.endpoints import (
    BASE_URL,
    DRIVERS,
    LIVE_FEED,
    LIVE_PITS,
    LIVE_POINTS,
    LIVE_STAGES,
    TRACKS,
    schedule_feed_path,
    schedule_path,
)
from custom_components.nascar_race_center.models import ProviderError


async def enable_scoring(hass, entry):
    registry = er.async_get(hass)
    # Let HA perform its real entity-enable reload immediately. Leaving the
    # normal 30-second reload queued would invalidate later expiry assertions.
    with patch("homeassistant.config_entries.RELOAD_AFTER_UPDATE_DELAY", 0):
        for suffix in (
            *(f"driver_99002_scoring_{key}" for key in FAVORITE_SCORING_METRICS),
            "1_scored_stages",
            "1_championship_leader",
        ):
            registry.async_update_entity(
                entity_id(hass, entry, suffix), disabled_by=None
            )
        await hass.async_block_till_done()
        async_fire_time_changed(hass)
        await hass.async_block_till_done()


async def scoring_refresh(hass, entry, *, stages=None, points=None, error=None):
    async def get(kind):
        if kind == "pits":
            return None
        if kind == "stages":
            return stages
        if error is not None:
            raise error
        return points

    provider = Mock()
    provider.async_get_scoring = AsyncMock(side_effect=get)
    entry.runtime_data.scoring.provider = provider
    await entry.runtime_data.scoring.async_refresh()
    await hass.async_block_till_done()
    return provider


async def test_embedded_entities_updates_missing_fields_and_opt_in_budget(
    hass, live_setup
):
    entry, provider = await live_setup(payload=embedded_payload())
    assert state(hass, entry, "1_current_stage").state == "2"
    assert state(hass, entry, "2_current_stage").state == STATE_UNAVAILABLE
    assert state(hass, entry, "1_pits_capability").attributes["embedded"] == "available"
    registry = er.async_get(hass)
    for key in FAVORITE_SCORING_METRICS:
        assert (
            registry.async_get(
                entity_id(hass, entry, f"driver_99002_scoring_{key}")
            ).disabled_by
            is not None
        )
    await enable_scoring(hass, entry)
    pit_id = entity_id(hass, entry, "driver_99002_scoring_pit_lap")
    pit = hass.states.get(pit_id)
    assert pit.state == "40"
    assert pit.attributes["entry_time_reported"] == 1280.5
    assert pit.attributes["exit_time_reported"] is None
    assert "unit_of_measurement" not in pit.attributes
    assert "pit_count" not in pit.attributes
    assert (
        state(hass, entry, "driver_99002_scoring_stage_position").state
        == STATE_UNAVAILABLE
    )
    payload = embedded_payload()
    payload["vehicles"][0]["pit_stops"][-1].update(
        pit_out_elapsed_time=1310.5, pit_out_rank=4, positions_gained_lossed=-2
    )
    await refresh(hass, entry, provider, payload)
    assert hass.states.get(pit_id).attributes["position_change"] == -2
    assert hass.states.get(pit_id).attributes["exit_time_reported"] == 1310.5
    payload["vehicles"][0]["pit_stops"] = []
    await refresh(hass, entry, provider, payload)
    assert hass.states.get(pit_id).state == STATE_UNKNOWN
    del payload["vehicles"][0]["pit_stops"]
    await refresh(hass, entry, provider, payload)
    assert hass.states.get(pit_id).state == STATE_UNAVAILABLE
    assert state(hass, entry, "driver_99002_live_position").state == "2"
    assert len(hass.states.get(pit_id).attributes) < 8


@pytest.mark.parametrize("series", [1, 2, 3])
async def test_stage_and_pit_series_switch_and_session_reset(hass, live_setup, series):
    payload = embedded_payload()
    payload["series_id"] = series
    entry, provider = await live_setup(payload=payload)
    await enable_scoring(hass, entry)
    assert state(hass, entry, f"{series}_current_stage").state == "2"
    assert (
        state(hass, entry, "driver_99002_scoring_pit_lap").attributes["series_id"]
        == series
    )
    payload.update(race_id=99123, run_id=9, run_type=1, stage=None, vehicles=[])
    await refresh(hass, entry, provider, payload)
    assert state(hass, entry, "driver_99002_scoring_pit_lap").state == STATE_UNAVAILABLE
    assert state(hass, entry, f"{series}_current_stage").state == STATE_UNAVAILABLE
    payload = embedded_payload()
    payload["series_id"] = series
    payload["stage"]["stage_num"] = 3
    await refresh(hass, entry, provider, payload)
    assert state(hass, entry, f"{series}_current_stage").state == "3"
    assert (
        "completed_stages"
        not in state(hass, entry, f"{series}_current_stage").attributes
    )


@pytest.mark.parametrize(
    "clock",
    [
        None,
        "bad",
        "2026-10-20T20:00:00",
        "2026-10-19T20:00:00Z",
        "2026-10-21T20:00:00Z",
    ],
)
async def test_embedded_scoring_requires_source_freshness(hass, live_setup, clock):
    payload = embedded_payload()
    payload["time_of_day_os"] = clock
    entry, _ = await live_setup(payload=payload)
    await enable_scoring(hass, entry)
    assert state(hass, entry, "1_current_stage").state == STATE_UNAVAILABLE
    assert state(hass, entry, "driver_99002_scoring_pit_lap").state == STATE_UNAVAILABLE
    assert entry.runtime_data.live.data.stage.number == 2  # diagnostics only


async def test_trusted_normalized_results_and_championship_updates_remain_provisional(
    hass, live_setup
):
    entry, provider = await live_setup(payload=embedded_payload())
    await enable_scoring(hass, entry)
    stages, points = trusted_feed("stages"), trusted_feed("points")
    await scoring_refresh(hass, entry, stages=stages, points=points)
    assert state(hass, entry, "1_scored_stages").state == "2"
    assert state(hass, entry, "driver_99002_scoring_stage_position").state == "12"
    assert (
        state(hass, entry, "driver_99002_scoring_stage_position").attributes[
            "stage_points"
        ]
        == 0
    )
    championship = state(hass, entry, "driver_99002_scoring_championship_position")
    assert (
        championship.state == "3"
        and championship.attributes["championship_points"] == 2040
    )
    assert championship.attributes["race_points"] == 31
    assert championship.attributes["bonus_points"] is None
    updated = replace(
        points,
        points=(replace(points.points[0], position=1, points=2043, race_points=None),),
    )
    await scoring_refresh(hass, entry, stages=stages, points=updated)
    assert state(hass, entry, "1_championship_leader").state == "99002"
    assert state(hass, entry, "driver_99002_scoring_championship_position").state == "1"
    assert (
        state(hass, entry, "driver_99002_scoring_championship_position").attributes[
            "race_points"
        ]
        is None
    )
    payload = embedded_payload()
    payload["flag_state"] = 5
    await refresh(hass, entry, provider, payload)
    assert state(hass, entry, "1_session_status").state == "completed"
    assert (
        state(hass, entry, "driver_99002_scoring_championship_position").attributes[
            "classification"
        ]
        == "provisional"
    )
    # Whole replacement: omitted rows/stages do not inherit earlier results.
    await scoring_refresh(
        hass,
        entry,
        stages=replace(stages, stages=stages.stages[:1]),
        points=replace(points, points=()),
    )
    assert state(hass, entry, "1_scored_stages").state == "1"
    assert state(hass, entry, "driver_99002_scoring_stage_position").state == "2"
    assert (
        state(hass, entry, "driver_99002_scoring_championship_position").state
        == STATE_UNAVAILABLE
    )


@pytest.mark.parametrize(
    "change",
    [
        {"race_id": 99999},
        {"run_id": 9},
        {"series_id": 2},
        {"run_type": 1},
        {"series_id": 3},
    ],
)
async def test_optional_scoring_never_attaches_to_next_race_or_session(
    hass, live_setup, change
):
    entry, provider = await live_setup(payload=embedded_payload())
    await enable_scoring(hass, entry)
    await scoring_refresh(
        hass, entry, stages=trusted_feed("stages"), points=trusted_feed("points")
    )
    assert state(hass, entry, "driver_99002_scoring_championship_position").state == "3"
    payload = embedded_payload()
    payload.update(change)
    await refresh(hass, entry, provider, payload)
    assert (
        state(hass, entry, "driver_99002_scoring_championship_position").state
        == STATE_UNAVAILABLE
    )
    assert (
        state(hass, entry, "driver_99002_scoring_stage_position").state
        == STATE_UNAVAILABLE
    )


@pytest.mark.parametrize("status", [403, 429, 503])
async def test_optional_feed_failure_is_independent_retained_and_recovers(
    hass, live_setup, freezer, status
):
    entry, _ = await live_setup(payload=embedded_payload())
    await enable_scoring(hass, entry)
    stages, points = trusted_feed("stages"), trusted_feed("points")
    await scoring_refresh(hass, entry, stages=stages, points=points)
    provider = await scoring_refresh(
        hass,
        entry,
        stages=stages,
        error=ProviderError("synthetic", status=status, retry_after=3600),
    )
    coordinator = entry.runtime_data.scoring
    assert coordinator.data.feeds["points"] is points
    assert state(hass, entry, "1_points_capability").state == (
        "denied" if status == 403 else "offline"
    )
    assert (
        state(hass, entry, "driver_99002_scoring_championship_position").state
        == STATE_UNAVAILABLE
    )
    assert state(hass, entry, "driver_99002_scoring_stage_position").state == "12"
    assert state(hass, entry, "driver_99002_live_position").state == "2"
    assert state(hass, entry, "1_current_stage").state == "2"
    assert state(hass, entry, "1_scheduled_races").state == "0"
    provider.async_get_scoring.reset_mock()
    await coordinator.async_refresh()
    assert [call.args[0] for call in provider.async_get_scoring.await_args_list] == [
        "pits",
        "stages",
    ]
    freezer.tick(timedelta(hours=1))
    await scoring_refresh(hass, entry, stages=stages, points=points)
    assert "points" not in coordinator.data.failed


async def test_independent_optional_expiry_without_http_and_clean_reload(
    hass, live_setup, freezer
):
    entry, provider = await live_setup(payload=embedded_payload())
    await enable_scoring(hass, entry)
    feed = trusted_feed("points", clock=NOW - timedelta(minutes=14))
    optional = await scoring_refresh(hass, entry, points=feed)
    assert state(hass, entry, "driver_99002_scoring_championship_position").state == "3"
    optional.async_get_scoring.reset_mock()
    freezer.tick(timedelta(minutes=2))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert state(hass, entry, "1_points_capability").state == "stale"
    assert (
        state(hass, entry, "driver_99002_scoring_championship_position").state
        == STATE_UNAVAILABLE
    )
    assert state(hass, entry, "driver_99002_scoring_pit_lap").state == "40"
    optional.async_get_scoring.assert_not_awaited()
    old = entry.runtime_data
    saved = entity_id(hass, entry, "driver_99002_scoring_pit_lap")
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert old.scoring._stopped and old.scoring._unsub_expiry is None
    assert not old.scoring._listeners and not old.live._listeners
    assert entity_id(hass, entry, "driver_99002_scoring_pit_lap") == saved
    assert not async_get_clientsession(hass).closed
    await old.scoring.async_request_refresh()
    optional.async_get_scoring.assert_not_awaited()


async def test_favorite_removal_cleans_only_recognized_scoring_entities(
    hass, live_setup
):
    entry, _ = await live_setup(payload=embedded_payload())
    ids = [
        entity_id(hass, entry, f"driver_99002_scoring_{key}")
        for key in FAVORITE_SCORING_METRICS
    ]
    hass.config_entries.async_update_entry(entry, options={CONF_FAVORITE_DRIVERS: []})
    await hass.async_block_till_done()
    for identifier in ids:
        assert er.async_get(hass).async_get(identifier) is None
    assert state(hass, entry, "1_current_stage").state == "2"


async def cf_entry(hass, aioclient_mock, *, pit_status=200):
    aioclient_mock.get(
        BASE_URL + schedule_path(2026), json={f"series_{s}": [] for s in (1, 2, 3)}
    )
    for series in (1, 2, 3):
        aioclient_mock.get(BASE_URL + schedule_feed_path(2026, series), json=[])
    aioclient_mock.get(BASE_URL + DRIVERS, status=503)
    aioclient_mock.get(BASE_URL + TRACKS, status=503)
    aioclient_mock.get(BASE_URL + LIVE_FEED, json=embedded_payload())
    aioclient_mock.get(BASE_URL + LIVE_PITS, json=fixture("pits"), status=pit_status)
    aioclient_mock.get(BASE_URL + LIVE_STAGES, json=fixture("stages"))
    aioclient_mock.get(BASE_URL + LIVE_POINTS, json=fixture("points"))
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PROVIDER: PROVIDER_CF,
            CONF_DATA_USE_AUTHORIZED: True,
            CONF_SERIES: ["1", "2", "3"],
            CONF_FAVORITE_DRIVERS: ["99002"],
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_cf_observed_global_conflicts_caching_and_small_diagnostics(
    hass, aioclient_mock, freezer
):
    freezer.move_to(NOW)
    entry = await cf_entry(hass, aioclient_mock)
    assert aioclient_mock.call_count == 10
    assert state(hass, entry, "1_pits_capability").state == "context_unknown"
    assert state(hass, entry, "1_stages_capability").state == "context_mismatch"
    assert state(hass, entry, "1_points_capability").state == "context_unknown"
    await entry.runtime_data.scoring.async_refresh()
    await entry.runtime_data.live.async_refresh()
    assert aioclient_mock.call_count == 10
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["scoring"]["feeds"]["points"]["points_rows"] == 1
    assert diagnostics["scoring"]["feeds"]["points"]["source_updated_at"] is None
    assert diagnostics["scoring"]["feeds"]["pits"]["contexts"] == []
    assert diagnostics["live"]["embedded_scoring"]["stage_reported"]
    assert "Synthetic Driver" not in str(diagnostics)
    assert len(str(diagnostics["scoring"])) < 4000
    assert entry.runtime_data.scoring.update_interval >= timedelta(minutes=15)
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize("status", [403, 429, 503])
async def test_cf_optional_access_rate_limit_and_server_failure(
    hass, aioclient_mock, freezer, status
):
    freezer.move_to(NOW)
    entry = await cf_entry(hass, aioclient_mock, pit_status=status)
    runtime = entry.runtime_data
    assert "pits" in runtime.scoring.data.failed
    assert state(hass, entry, "1_current_stage").state == "2"
    assert state(hass, entry, "driver_99002_live_position").state == "2"
    if status == 429:
        assert runtime.scoring.data.failed == {"pits", "stages", "points"}
        assert aioclient_mock.call_count == 8  # host-wide pause suppresses next GETs
    else:
        assert runtime.scoring.data.failed == {"pits"}
        assert aioclient_mock.call_count == 10
    before = aioclient_mock.call_count
    await runtime.scoring.async_refresh()
    assert aioclient_mock.call_count == before
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_inflight_optional_refresh_cannot_rearm_after_shutdown(hass, live_setup):
    entry, _ = await live_setup(payload=embedded_payload())
    coordinator = entry.runtime_data.scoring
    started, release = asyncio.Event(), asyncio.Event()

    async def delayed(kind):
        started.set()
        await release.wait()
        return trusted_feed("points") if kind == "points" else None

    coordinator.provider = Mock(async_get_scoring=AsyncMock(side_effect=delayed))
    task = asyncio.create_task(coordinator.async_refresh())
    try:
        await started.wait()
        assert await hass.config_entries.async_unload(entry.entry_id)
    finally:
        release.set()
        await task
    assert coordinator._unsub_expiry is None and coordinator._stopped
    assert not coordinator._listeners


async def test_optional_cancellation_propagates_and_retains_baseline(hass, live_setup):
    entry, _ = await live_setup(payload=embedded_payload())
    await scoring_refresh(hass, entry, points=trusted_feed("points"))
    coordinator = entry.runtime_data.scoring
    saved = coordinator.data
    coordinator.provider.async_get_scoring.side_effect = asyncio.CancelledError
    # HA catches refresh cancellation, while the provider/coordinator boundary
    # propagates it. No partial feed snapshot may replace the baseline.
    await coordinator.async_refresh()
    assert coordinator.data is saved


async def test_recorder_suppresses_timestamp_and_other_driver_scoring_changes(
    recorder_mock, hass, live_setup, freezer
):
    from homeassistant.components.recorder.db_schema import States, StatesMeta
    from pytest_homeassistant_custom_component.components.recorder.common import (
        async_wait_recording_done,
    )
    from sqlalchemy import func, select

    entry, provider = await live_setup(payload=embedded_payload())
    await enable_scoring(hass, entry)
    watched = (
        entity_id(hass, entry, "driver_99002_scoring_pit_lap"),
        entity_id(hass, entry, "1_current_stage"),
    )

    def counts():
        with recorder_mock.get_session() as session:
            return dict(
                session.execute(
                    select(StatesMeta.entity_id, func.count(States.state_id))
                    .join(States, States.metadata_id == StatesMeta.metadata_id)
                    .where(StatesMeta.entity_id.in_(watched))
                    .group_by(StatesMeta.entity_id)
                ).all()
            )

    await async_wait_recording_done(hass)
    baseline = await hass.async_add_executor_job(counts)
    for index in range(5):
        freezer.tick(timedelta(seconds=1))
        payload = embedded_payload()
        payload["time_of_day_os"] = f"2026-10-20T20:00:{index + 1:02d}Z"
        payload["vehicles"][1]["last_lap_time"] = 31 + index
        await refresh(hass, entry, provider, payload)
    await async_wait_recording_done(hass)
    assert await hass.async_add_executor_job(counts) == baseline
    payload["vehicles"][0]["pit_stops"][-1]["pit_out_elapsed_time"] = 1310.5
    await refresh(hass, entry, provider, payload)
    await async_wait_recording_done(hass)
    updated = await hass.async_add_executor_job(counts)
    assert updated[watched[0]] == baseline[watched[0]] + 1
    assert updated[watched[1]] == baseline[watched[1]]
