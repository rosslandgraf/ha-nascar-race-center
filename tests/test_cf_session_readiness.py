"""All-series/session CF-shaped replay through real HA; every HTTP call intercepted."""

from copy import deepcopy
from datetime import timedelta

import pytest
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import MockConfigEntry
from test_cf_diagnostics import fixture
from test_dashboard_websocket import call
from test_live_timing import timing_payload

from custom_components.nascar_race_center.const import (
    CONF_DATA_USE_AUTHORIZED,
    CONF_FAVORITE_DRIVERS,
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    PROVIDER_CF,
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

pytestmark = pytest.mark.freeze_time("2026-10-22T18:00:00Z")


async def setup(hass, aioclient_mock, payload):
    aioclient_mock.get(BASE_URL + schedule_path(2026), json=fixture("schedule"))
    for series in (1, 2, 3):
        aioclient_mock.get(BASE_URL + schedule_feed_path(2026, series), json=[])
    aioclient_mock.get(BASE_URL + DRIVERS, json=fixture("drivers"))
    aioclient_mock.get(BASE_URL + TRACKS, json=fixture("tracks"))
    aioclient_mock.get(BASE_URL + LIVE_FEED, json=payload)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PROVIDER: PROVIDER_CF,
            CONF_SERIES: ["1", "2", "3"],
            CONF_FAVORITE_DRIVERS: ["99002"],
            CONF_DATA_USE_AUTHORIZED: True,
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def live_data(hass, hass_ws_client, entry, series):
    # Close before advancing frozen time so no real WS heartbeat outlives its client.
    client = await hass_ws_client(hass)
    try:
        return (await call(client, entry, "live", series_id=series))["result"]["data"]
    finally:
        await client.close()


@pytest.mark.parametrize("series", [1, 2, 3])
@pytest.mark.parametrize("kind,name", [(1, "practice"), (2, "qualifying"), (3, "race")])
async def test_every_session_reaches_real_websocket_and_favorites(
    hass, aioclient_mock, hass_ws_client, freezer, series, kind, name
):
    payload = timing_payload()
    for index in range(4, 41):
        row = deepcopy(payload["vehicles"][0])
        row.update(running_position=index, vehicle_number=str(index))
        row["driver"].update(driver_id=99000 + index, full_name=f"Fictional {index}")
        payload["vehicles"].append(row)
    payload.update(
        series_id=series,
        run_type=kind,
        lap_number=0 if kind != 3 else 42,
        time_of_day_os=dt_util.utcnow().isoformat(),
    )
    if kind != 3:
        # Community-documented non-race sentinels must not become race scoring.
        payload.update(
            laps_in_race=999,
            laps_to_go=999,
            stage={"stage_num": 999, "finish_at_lap": 999, "laps_in_stage": 999},
        )
    entry = await setup(hass, aioclient_mock, payload)
    data = await live_data(hass, hass_ws_client, entry, series)
    assert data["session"]["status"] == name
    assert data["session_state"] == "activity_unconfirmed"
    assert len(data["leaderboard"]) == 40
    assert data["leaderboard"][1]["favorite"]
    assert data["leaderboard"][1]["car_number"] == "07"
    assert data["session"]["total_laps"] == (100 if kind == 3 else None)
    assert data["session"]["stage"] is None
    for other in {1, 2, 3} - {series}:
        row = await live_data(hass, hass_ws_client, entry, other)
        assert row["leaderboard"] is None and row["availability"] == "not_reported"
    assert aioclient_mock.call_count == 7
    # Multiple cards/manual refreshes reuse the shared cache, not a new sample.
    await entry.runtime_data.live.async_refresh()
    assert entry.runtime_data.live.observation_state == "first_observation"
    assert aioclient_mock.call_count == 7
    # Advance by the real CF floor; progression uses driver observations, not clocks.
    freezer.tick(301)
    payload["time_of_day_os"] = dt_util.utcnow().isoformat()
    payload["vehicles"][0]["laps_completed"] += 1
    aioclient_mock.clear_requests()
    aioclient_mock.get(BASE_URL + LIVE_FEED, json=payload)
    await entry.runtime_data.live.async_refresh()
    data = await live_data(hass, hass_ws_client, entry, series)
    assert data["session_state"] == "active"
    assert data["observation_advancement"] == "observations_changed"
    assert entry.runtime_data.live.update_interval == timedelta(seconds=300)
    assert aioclient_mock.call_count == 1
    for collection in ("pits", "stages", "points"):
        assert data["scoring"][collection]["records"] is None
    await entry.runtime_data.live.async_refresh()
    assert entry.runtime_data.live.view(series).session_status == "active"
    assert aioclient_mock.call_count == 1


@pytest.mark.parametrize(
    "mode",
    [
        "empty",
        "cold",
        "timestamp_only",
        "metadata_only",
        "clock_unchanged",
        "stale",
        "regressed",
        "missing_run",
        "bad_flag",
        "kind_change",
    ],
)
async def test_retained_and_ambiguous_source_never_claims_active(
    hass, aioclient_mock, hass_ws_client, freezer, mode
):
    payload = timing_payload()
    payload["time_of_day_os"] = dt_util.utcnow().isoformat()
    entry = await setup(hass, aioclient_mock, payload)
    freezer.tick(301)
    payload["time_of_day_os"] = dt_util.utcnow().isoformat()
    if mode == "clock_unchanged":
        payload["time_of_day_os"] = (
            entry.runtime_data.live.data.source_updated_at.isoformat()
        )
    if mode == "stale":
        payload["time_of_day_os"] = (
            dt_util.utcnow() - timedelta(seconds=901)
        ).isoformat()
    if mode == "empty":
        payload["vehicles"] = []
    if mode == "metadata_only":
        payload["run_name"] = "Corrected fictional name"
        payload["elapsed_time"] += 301
        payload["vehicles"][0]["driver"]["full_name"] = "Corrected fictional driver"
        payload["vehicles"][0]["vehicle_number"] = "09"
    if mode == "cold":
        payload["flag_state"] = 9
    if mode == "regressed":
        payload["time_of_day_os"] = (
            dt_util.utcnow() - timedelta(seconds=302)
        ).isoformat()
    if mode == "missing_run":
        payload.pop("run_id")
    if mode == "bad_flag":
        payload["flag_state"] = 99
    if mode == "kind_change":
        payload.update(run_type=2, lap_number=0)
    aioclient_mock.clear_requests()
    aioclient_mock.get(BASE_URL + LIVE_FEED, json=payload)
    await entry.runtime_data.live.async_refresh()
    data = await live_data(hass, hass_ws_client, entry, 1)
    assert data["session_state"] != "active"
    if mode not in {"bad_flag", "kind_change"}:
        assert data["leaderboard"] is None
    if mode == "kind_change":
        assert data["session_state"] == "activity_unconfirmed"
        assert data["session"]["status"] == "qualifying"
    if mode == "missing_run":
        assert data["session_state"] == "observations_unavailable"
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["live"]["timing"]["reported_count"] == (
        0 if mode == "empty" else 3
    )
    assert (
        diagnostics["cf_pipeline"]["transport"][LIVE_FEED]["next_eligible_in_seconds"]
        > 0
    )
    assert aioclient_mock.call_count == 1


async def test_real_cf_session_transition_completion_expiry_and_reload(
    hass, aioclient_mock, hass_ws_client, freezer
):
    payload = timing_payload()
    payload["time_of_day_os"] = dt_util.utcnow().isoformat()
    entry = await setup(hass, aioclient_mock, payload)

    async def refresh(**changes):
        freezer.tick(301)
        payload.update(time_of_day_os=dt_util.utcnow().isoformat(), **changes)
        aioclient_mock.clear_requests()
        aioclient_mock.get(BASE_URL + LIVE_FEED, json=payload)
        await entry.runtime_data.live.async_refresh()
        assert aioclient_mock.call_count == 1
        return await live_data(hass, hass_ws_client, entry, payload["series_id"])

    assert (await refresh(lap_number=43))["session_state"] == "active"
    empty = await refresh(vehicles=[])
    assert empty["session_state"] == "no_active_session"
    assert empty["leaderboard"] is None
    # Same timestamp cannot prove another session active; no prior field is merged.
    new = await refresh(
        series_id=3,
        race_id=99012,
        run_id=8,
        run_type=2,
        lap_number=0,
        vehicles=timing_payload()["vehicles"],
    )
    assert new["identity"]["race_id"] == "99012"
    assert new["session_state"] == "activity_unconfirmed"
    assert (await live_data(hass, hass_ws_client, entry, 1))["leaderboard"] is None
    completed = await refresh(flag_state=5)
    assert completed["session_state"] == "completed"
    assert completed["leaderboard"] is not None
    unchanged = await refresh()
    assert unchanged["session_state"] == "completed"
    assert unchanged["leaderboard"] is None
    old = entry.runtime_data
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert old.live._stopped and old.scoring._stopped
    assert not old.live._listeners and not old.schedule._listeners
    # Reload within the next reserved slot reuses the provider cache.
    aioclient_mock.clear_requests()
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert aioclient_mock.call_count == 0
    assert entry.runtime_data.live.view(3).session_status == "completed"
    freezer.tick(901)
    assert entry.runtime_data.live.view(3).health == "stale"
