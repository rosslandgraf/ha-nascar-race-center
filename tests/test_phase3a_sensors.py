"""Replay synthetic fields through real HA platforms, lifecycle and Recorder."""

from dataclasses import replace
from datetime import timedelta
from unittest.mock import AsyncMock, Mock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from test_live_timing import timing_payload

from custom_components.nascar_race_center.const import (
    CONF_DATA_USE_AUTHORIZED,
    CONF_FAVORITE_DRIVERS,
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    FAVORITE_LIVE_METRICS,
    PROVIDER_CF,
    PROVIDER_DEMO,
)
from custom_components.nascar_race_center.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.nascar_race_center.endpoints import (
    BASE_URL,
    DRIVERS,
    LIVE_FEED,
    TRACKS,
    schedule_feed_path,
    schedule_path,
)
from custom_components.nascar_race_center.models import ProviderError, parse_live


def entity_id(hass, entry, suffix):
    result = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_{suffix}"
    )
    assert result is not None
    return result


def state(hass, entry, suffix):
    result = hass.states.get(entity_id(hass, entry, suffix))
    assert result is not None
    return result


@pytest.fixture
async def live_setup(hass: HomeAssistant, freezer):
    """Only I/O is replaced; HA owns platforms, listeners, reloads and timers."""
    freezer.move_to("2026-10-20T20:00:00Z")
    provider = Mock()
    provider.async_get_schedule = AsyncMock(return_value=())
    provider.async_get_live = AsyncMock(return_value=parse_live(timing_payload()))
    entries = []

    async def setup(*, favorites=("99002",), series=("1", "2", "3"), payload=None):
        if payload is not None:
            provider.async_get_live.return_value = parse_live(payload)
        entry = MockConfigEntry(
            domain=DOMAIN,
            data={
                CONF_PROVIDER: PROVIDER_DEMO,
                CONF_SERIES: list(series),
                CONF_FAVORITE_DRIVERS: list(favorites),
            },
        )
        entry.add_to_hass(hass)
        entries.append(entry)
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        return entry, provider

    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        yield setup
        for entry in entries:
            if entry.state is ConfigEntryState.LOADED:
                assert await hass.config_entries.async_unload(entry.entry_id)
                await hass.async_block_till_done()


async def refresh(hass, entry, provider, payload):
    provider.async_get_live.return_value = parse_live(payload)
    await entry.runtime_data.live.async_refresh()
    await hass.async_block_till_done()


async def enable_metrics(hass, entry, driver_id=99002):
    registry = er.async_get(hass)
    for key in FAVORITE_LIVE_METRICS:
        registry.async_update_entity(
            entity_id(hass, entry, f"driver_{driver_id}_live_{key}"), disabled_by=None
        )
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()


async def test_real_entities_report_scoring_and_reuse_single_source(hass, live_setup):
    entry, provider = await live_setup()
    assert state(hass, entry, "1_leader").state == "99001"
    assert (
        state(hass, entry, "1_leader").attributes["driver_name"] == "Synthetic Driver A"
    )
    assert state(hass, entry, "1_total_laps").state == "100"
    assert state(hass, entry, "1_laps_remaining").state == "58"
    assert state(hass, entry, "1_session_status").state == "active"
    assert state(hass, entry, "driver_99002_live_position").state == "2"
    assert state(hass, entry, "2_session_status").state == "not_reported"
    assert state(hass, entry, "3_leader").state == STATE_UNAVAILABLE
    provider.async_get_live.assert_awaited_once()
    registry = er.async_get(hass)
    for key in FAVORITE_LIVE_METRICS:
        entity = registry.async_get(entity_id(hass, entry, f"driver_99002_live_{key}"))
        assert (entity.disabled_by is None) == (key == "position")
    # The full field never creates nonfavorite driver entities or attributes.
    assert not any(
        "driver_99001_" in entity.unique_id for entity in registry.entities.values()
    )
    assert len(entry.runtime_data.live.view(1).leaderboard.drivers) == 3
    assert entry.runtime_data.live.view(2).leaderboard is None
    assert "drivers" not in state(hass, entry, "1_leader").attributes
    assert len(state(hass, entry, "driver_99002_live_position").attributes) < 10


async def test_optional_timing_sensors_enabled_through_registry(hass, live_setup):
    entry, _ = await live_setup()
    await enable_metrics(hass, entry)
    for key, expected in (
        ("last_lap", "31.25"),
        ("best_lap", "30.5"),
        ("gap", "0.75"),
        ("running_status", "running"),
        ("position_change", "3"),
    ):
        assert state(hass, entry, f"driver_99002_live_{key}").state == expected
    assert (
        state(hass, entry, "driver_99002_live_last_lap").attributes[
            "unit_of_measurement"
        ]
        == "s"
    )
    assert (
        "unit_of_measurement"
        not in state(hass, entry, "driver_99002_live_gap").attributes
    )


@pytest.mark.parametrize(
    "timestamp",
    [None, "bad", "2026-10-20T20:00:00", "2026-10-21T20:00:00Z"],
    ids=["missing", "malformed", "offset_free", "future"],
)
async def test_unknown_freshness_gates_scoring_at_setup_refresh_and_reload(
    hass, live_setup, timestamp
):
    payload = {**timing_payload(), "time_of_day_os": timestamp}
    entry, provider = await live_setup(payload=payload)
    saved_id = entity_id(hass, entry, "driver_99002_live_position")
    assert hass.states.get(saved_id).state == STATE_UNAVAILABLE
    registry = er.async_get(hass)
    registry.async_update_entity(
        entity_id(hass, entry, "1_field_size"), disabled_by=None
    )
    await enable_metrics(hass, entry)  # Also reloads with unknown source freshness.

    for recovering in (False, True, False, True):
        await refresh(
            hass, entry, provider, timing_payload() if recovering else payload
        )
        view = entry.runtime_data.live.view(1)
        assert view.health == ("ok" if recovering else "freshness_unknown")
        assert view.available is recovering
        assert (view.leaderboard is not None) is recovering
        assert (view.driver(99002) is not None) is recovering
        for key, expected in (
            ("leader", "99001"),
            ("total_laps", "100"),
            ("laps_remaining", "58"),
            ("field_size", "3"),
        ):
            assert state(hass, entry, f"1_{key}").state == (
                expected if recovering else STATE_UNAVAILABLE
            )
        for key, expected in (
            ("position", "2"),
            ("last_lap", "31.25"),
            ("best_lap", "30.5"),
            ("gap", "0.75"),
            ("running_status", "running"),
            ("position_change", "3"),
        ):
            assert state(hass, entry, f"driver_99002_live_{key}").state == (
                expected if recovering else STATE_UNAVAILABLE
            )
        assert entity_id(hass, entry, "driver_99002_live_position") == saved_id
        # Keep diagnostic context and Phase 1/2 behavior independent of scoring.
        assert entry.runtime_data.live.data.leaderboard.by_driver[99002].position == 2
        assert state(hass, entry, "1_feed_status").state == view.health
        assert state(hass, entry, "1_session_status").state == (
            "active" if recovering else STATE_UNKNOWN
        )
        assert state(hass, entry, "1_flag").state == "green"
        assert state(hass, entry, "1_current_lap").state == "42"
        assert state(hass, entry, "1_scheduled_races").state == "0"
        assert state(hass, entry, "driver_99002_metadata").state != STATE_UNAVAILABLE
        assert entry.runtime_data.live.view(2).leaderboard is None


async def test_replay_positions_lead_runs_races_series_and_unreported_driver(
    hass, live_setup
):
    entry, provider = await live_setup()
    saved_id = entity_id(hass, entry, "driver_99002_live_position")
    device_id = er.async_get(hass).async_get(saved_id).device_id
    payload = timing_payload()
    payload["vehicles"][0].update(running_position=1, vehicle_number="19")
    payload["vehicles"][0]["driver"]["full_name"] = "Renamed Synthetic B"
    payload["vehicles"][1]["running_position"] = 2
    await refresh(hass, entry, provider, payload)
    assert state(hass, entry, "1_leader").state == "99002"
    assert hass.states.get(saved_id).state == "1"
    for series_id in (2, 3, 1):
        payload.update(series_id=series_id, race_id=99001 + series_id, run_id=8)
        await refresh(hass, entry, provider, payload)
        assert hass.states.get(saved_id).attributes["series_id"] == series_id
        assert state(hass, entry, f"{series_id}_leader").state == "99002"
        assert (
            sum(
                entry.runtime_data.live.view(series).leaderboard is not None
                for series in (1, 2, 3)
            )
            == 1
        )
    assert er.async_get(hass).async_get(saved_id).device_id == device_id
    payload.update(run_id=9, run_type=1, lap_number=0, vehicles=[])
    await refresh(hass, entry, provider, payload)
    assert state(hass, entry, "1_session_status").state == "no_active_session"
    assert hass.states.get(saved_id).state == STATE_UNAVAILABLE
    assert entry.runtime_data.live.data.session_key == (1, 99002, 9)
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert entity_id(hass, entry, "driver_99002_live_position") == saved_id


@pytest.mark.parametrize(
    ("changes", "progress", "health", "leader"),
    [
        ({"flag_state": 5, "laps_to_go": 0}, "completed", "ok", "99001"),
        ({"flag_state": 2}, "active", "ok", "99001"),
        ({"flag_state": 3}, "active", "ok", "99001"),
        ({"flag_state": 99}, STATE_UNKNOWN, "ok", "99001"),
        ({"flag_state": 9}, "latest_recorded", "ok", STATE_UNAVAILABLE),
        ({"lap_number": 0}, STATE_UNKNOWN, "ok", "99001"),
        (
            {"time_of_day_os": None},
            STATE_UNKNOWN,
            "freshness_unknown",
            STATE_UNAVAILABLE,
        ),
        (
            {"time_of_day_os": "2026-10-21T20:00:00Z"},
            STATE_UNKNOWN,
            "freshness_unknown",
            STATE_UNAVAILABLE,
        ),
        (
            {"time_of_day_os": "2026-10-19T20:00:00Z"},
            "stale",
            "stale",
            STATE_UNAVAILABLE,
        ),
        (
            {"time_of_day_os": "2026-10-19T20:00:00Z", "flag_state": 5},
            "stale",
            "stale",
            STATE_UNAVAILABLE,
        ),
    ],
)
async def test_progress_requires_source_evidence(
    hass, live_setup, changes, progress, health, leader
):
    entry, provider = await live_setup()
    await refresh(hass, entry, provider, {**timing_payload(), **changes})
    assert state(hass, entry, "1_session_status").state == progress
    assert state(hass, entry, "1_feed_status").state == health
    assert state(hass, entry, "1_leader").state == leader


async def test_unknown_fields_and_scoring_drift_keep_race_and_reference_usable(
    hass, live_setup
):
    entry, provider = await live_setup()
    await enable_metrics(hass, entry)
    payload = timing_payload()
    payload["vehicles"][0] = {"driver": {"driver_id": 99002}, "status": 99}
    payload.pop("laps_to_go")
    await refresh(hass, entry, provider, payload)
    assert state(hass, entry, "driver_99002_live_position").state == STATE_UNKNOWN
    assert state(hass, entry, "driver_99002_live_last_lap").state == STATE_UNKNOWN
    assert state(hass, entry, "driver_99002_live_running_status").state == STATE_UNKNOWN
    assert state(hass, entry, "1_laps_remaining").state == STATE_UNKNOWN
    payload["vehicles"] = {"unrecognized": "shape"}
    await refresh(hass, entry, provider, payload)
    assert state(hass, entry, "driver_99002_live_position").state == STATE_UNAVAILABLE
    assert state(hass, entry, "1_leader").state == STATE_UNAVAILABLE
    assert state(hass, entry, "1_current_lap").state == "42"
    assert state(hass, entry, "1_flag").state == "green"
    assert state(hass, entry, "1_scheduled_races").state == "0"
    assert state(hass, entry, "driver_99002_metadata").state != STATE_UNAVAILABLE
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["live"]["timing"]["status"] == "invalid"
    assert "vehicles" not in str(diagnostics)


async def test_live_tracking_does_not_depend_on_driver_directory(hass, live_setup):
    entry, _ = await live_setup(favorites=("99002", "99999"))
    reference = entry.runtime_data.reference
    reference.async_set_updated_data(
        replace(reference.data, failed_feeds=frozenset({"drivers"}))
    )
    await hass.async_block_till_done()
    assert state(hass, entry, "driver_99002_metadata").state == STATE_UNAVAILABLE
    assert state(hass, entry, "driver_99002_live_position").state == "2"
    assert state(hass, entry, "driver_99999_live_position").state == STATE_UNAVAILABLE
    assert entry.runtime_data.favorites.ids == (99002, 99999)


async def test_unselected_series_and_empty_feed_never_reuse_scoring(hass, live_setup):
    entry, provider = await live_setup(series=("1",))
    await refresh(hass, entry, provider, {**timing_payload(), "series_id": 2})
    assert state(hass, entry, "driver_99002_live_position").state == STATE_UNAVAILABLE
    assert entry.runtime_data.live.view(2).leaderboard is None
    await refresh(hass, entry, provider, None)
    assert state(hass, entry, "1_session_status").state == "no_active_session"
    assert state(hass, entry, "1_leader").state == STATE_UNAVAILABLE


@pytest.mark.parametrize("status", [403, 429, 503])
async def test_live_failure_retention_health_retry_and_recovery(
    hass, live_setup, status
):
    entry, provider = await live_setup()
    coordinator = entry.runtime_data.live
    saved = coordinator.data
    provider.async_get_live.side_effect = ProviderError(
        "Synthetic outage", status=status, retry_after=3600
    )
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert coordinator.data is saved
    assert coordinator.view(1).leaderboard is None
    assert state(hass, entry, "driver_99002_live_position").state == STATE_UNAVAILABLE
    assert state(hass, entry, "1_session_status").state == STATE_UNAVAILABLE
    assert state(hass, entry, "1_feed_status").state == (
        "denied" if status == 403 else "offline"
    )
    assert state(hass, entry, "1_scheduled_races").state == "0"
    assert coordinator.update_interval >= timedelta(hours=1)
    provider.async_get_live.side_effect = None
    await refresh(hass, entry, provider, timing_payload())
    assert state(hass, entry, "driver_99002_live_position").state == "2"


async def test_local_expiry_and_reload_stop_old_listeners_and_shared_session(
    hass, live_setup, freezer
):
    entry, provider = await live_setup()
    old = entry.runtime_data
    saved_id = entity_id(hass, entry, "driver_99002_live_position")
    payload = timing_payload()
    payload["lap_number"] = 0  # Keeps the poll later than local source expiry.
    await refresh(hass, entry, provider, payload)
    provider.async_get_live.reset_mock()
    freezer.tick(timedelta(minutes=16))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert hass.states.get(saved_id).state == STATE_UNAVAILABLE
    assert state(hass, entry, "1_session_status").state == "stale"
    provider.async_get_live.assert_not_awaited()
    payload["time_of_day_os"] = "2026-10-20T20:16:00Z"
    await refresh(hass, entry, provider, payload)
    assert hass.states.get(saved_id).state == "2"
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert old.live._stopped
    assert not old.live._listeners
    assert old.live._unsub_source_expiry is None
    assert entity_id(hass, entry, "driver_99002_live_position") == saved_id
    assert not async_get_clientsession(hass).closed
    replacement = entry.runtime_data
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert not replacement.live._listeners
    assert hass.states.get(saved_id).state == STATE_UNAVAILABLE
    assert hass.states.get(saved_id).attributes["restored"] is True


async def test_cf_structural_timing_setup_uses_only_existing_seven_endpoints(
    hass, aioclient_mock, freezer
):
    freezer.move_to("2026-10-20T20:00:00Z")
    aioclient_mock.get(
        BASE_URL + schedule_path(2026), json={f"series_{i}": [] for i in (1, 2, 3)}
    )
    for series_id in (1, 2, 3):
        aioclient_mock.get(BASE_URL + schedule_feed_path(2026, series_id), json=[])
    aioclient_mock.get(BASE_URL + DRIVERS, status=503)
    aioclient_mock.get(BASE_URL + TRACKS, status=503)
    aioclient_mock.get(BASE_URL + LIVE_FEED, json=timing_payload())
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
    assert state(hass, entry, "driver_99002_live_position").state == "2"
    assert state(hass, entry, "driver_99002_metadata").state == STATE_UNAVAILABLE
    assert state(hass, entry, "1_leader").state == "99001"
    assert aioclient_mock.call_count == 7
    await entry.runtime_data.live.async_refresh()
    await hass.async_block_till_done()
    assert aioclient_mock.call_count == 7  # Transport TTL shared by all entities.
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["live"]["timing"]["normalized_count"] == 3
    assert diagnostics["live"]["timing"]["field_counts"]["last_lap_time"] == 2
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.fixture
def mock_recorder_before_hass(request):
    """Recorder's database must exist before HA's fixture starts."""
    if "recorder_mock" in request.fixturenames:
        request.getfixturevalue("recorder_db_url")


async def test_recorder_ignores_unchanged_favorites_other_drivers_and_source_clock(
    recorder_mock, hass, live_setup, freezer
):
    """Measure actual database writes across repeated whole-field refreshes."""
    from homeassistant.components.recorder.db_schema import States, StatesMeta
    from pytest_homeassistant_custom_component.components.recorder.common import (
        async_wait_recording_done,
    )
    from sqlalchemy import func, select

    entry, provider = await live_setup()
    favorite = entity_id(hass, entry, "driver_99002_live_position")
    current_lap = entity_id(hass, entry, "1_current_lap")
    leader = entity_id(hass, entry, "1_leader")
    watched = (favorite, current_lap, leader)

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
    before = await hass.async_add_executor_job(counts)
    assert all(before.get(entity, 0) >= 1 for entity in watched)
    payload = timing_payload()
    for index in range(10):
        freezer.tick(timedelta(seconds=1))
        # Source advances and another competitor's timing changes. These are
        # not state changes for the favorite, current lap or leader.
        payload["time_of_day_os"] = f"2026-10-20T20:00:{index + 1:02d}Z"
        payload["vehicles"][1]["last_lap_time"] = 30 + index / 10
        await refresh(hass, entry, provider, payload)
    await async_wait_recording_done(hass)
    assert await hass.async_add_executor_job(counts) == before
    payload["vehicles"][0]["running_position"] = 3
    await refresh(hass, entry, provider, payload)
    await async_wait_recording_done(hass)
    after = await hass.async_add_executor_job(counts)
    assert after[favorite] == before[favorite] + 1
    assert after[current_lap] == before[current_lap]
    assert after[leader] == before[leader]


@pytest.mark.parametrize("flag_state", [0, 8, 9, 99])
async def test_unknown_or_track_only_flags_do_not_accelerate_polling(
    hass, live_setup, flag_state
):
    entry, provider = await live_setup()
    await refresh(hass, entry, provider, {**timing_payload(), "flag_state": flag_state})
    assert state(hass, entry, "1_session_status").state == (
        "latest_recorded" if flag_state == 9 else STATE_UNKNOWN
    )
    assert entry.runtime_data.live.update_interval >= timedelta(hours=6)


async def test_fifty_favorites_bound_enabled_entities_without_extra_polls(
    hass, live_setup
):
    selected = tuple(str(driver_id) for driver_id in range(99001, 99051))
    entry, provider = await live_setup(favorites=selected)
    entries = [
        entity
        for entity in er.async_get(hass).entities.values()
        if entity.config_entry_id == entry.entry_id and "_live_" in entity.unique_id
    ]
    assert len(entries) == 50 * len(FAVORITE_LIVE_METRICS)
    assert sum(entity.disabled_by is None for entity in entries) == 50
    provider.async_get_live.assert_awaited_once()
    assert len(entry.runtime_data.live.data.leaderboard.drivers) == 3
