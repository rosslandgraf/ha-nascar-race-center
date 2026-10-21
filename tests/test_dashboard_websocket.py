"""Actual authenticated HA WebSocket server/clients; all NASCAR data is synthetic."""

import asyncio
import json
from dataclasses import replace
from datetime import timedelta
from unittest.mock import AsyncMock

import pytest
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed
from test_dashboard import historical
from test_init import demo_entry
from test_phase3b_setup import cf_entry
from test_scoring import embedded_payload

from custom_components.nascar_race_center import dashboard
from custom_components.nascar_race_center.const import CONF_FAVORITE_DRIVERS
from custom_components.nascar_race_center.history_models import HistoryDataset
from custom_components.nascar_race_center.models import parse_live
from custom_components.nascar_race_center.websocket import PREFIX


@pytest.fixture
async def dashboard_entry(hass):
    entry = demo_entry(["1", "2"])
    entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        entry, options={CONF_FAVORITE_DRIVERS: ["99002"]}
    )
    assert await hass.config_entries.async_setup(entry.entry_id)
    return entry


def message(entry, command, **kwargs):
    return {
        "type": PREFIX + command,
        "entry_id": entry.entry_id,
        "api_version": 1,
        **kwargs,
    }


async def call(client, entry, command, **kwargs):
    await client.send_json_auto_id(message(entry, command, **kwargs))
    return await client.receive_json()


async def receive_update(client):
    async with asyncio.timeout(2):
        result = await client.receive_json()
    assert result["type"] == "event"
    return result["event"]["data"]


def set_live(entry, **changes):
    payload = embedded_payload()
    payload["time_of_day_os"] = dt_util.utcnow().isoformat()
    payload.update(changes)
    snapshot = parse_live(payload)
    entry.runtime_data.live.async_set_updated_data(snapshot)
    entry.runtime_data.live._schedule_source_expiry(snapshot)
    return snapshot


async def test_authenticated_bootstrap_cached_references_and_series(
    hass, dashboard_entry, hass_ws_client
):
    client = await hass_ws_client(hass)
    output = await call(client, dashboard_entry, "bootstrap")
    assert output["success"]
    assert output["result"]["api_version"] == 1
    data = output["result"]["data"]
    assert data["series_ids"] == [1, 2]
    assert data["favorite_driver_ids"] == ["99002"]
    assert all(r["series_id"] in [1, 2] for r in data["upcoming"])
    assert len(json.dumps(output)) < 16_384
    assert data["capabilities"]["access"] == "administrator"
    schedule = await call(client, dashboard_entry, "schedule", series_id=1)
    assert schedule["success"]
    assert schedule["result"]["data"]["catalog_scope"] == "retained_supported_schedules"


@pytest.mark.parametrize(
    "command", ["bootstrap", "live", "subscribe_live", "history", "analytics"]
)
async def test_restricted_user_denied_all_data(
    hass, dashboard_entry, hass_ws_client, hass_read_only_access_token, command
):
    client = await hass_ws_client(hass, access_token=hass_read_only_access_token)
    kwargs = {}
    if command != "bootstrap":
        kwargs["series_id"] = 1
    if command in ("history", "analytics"):
        kwargs.update(season=2024, race_id=88001, datasets=["laps"])
    if command == "analytics":
        kwargs.update(
            driver_ids=[99002],
            first_lap=1,
            last_lap=10,
            windows=[5],
            time_basis="all_available",
        )
    result = await call(client, dashboard_entry, command, **kwargs)
    assert result["error"]["code"] == "unauthorized"
    assert not dashboard_entry.runtime_data.dashboard.subscriptions


@pytest.mark.parametrize(
    "changes",
    [
        {"series_id": 3},
        {"series_id": True},
        {"series_id": "1"},
        {"season": 1947},
        {"race_id": 0},
        {"race_id": True},
        {"datasets": []},
        {"datasets": ["laps", "laps"]},
        {"datasets": ["credentials"]},
        {"limit": 201},
        {"limit": False},
        {"offset": -1},
        {"snapshot": "bad"},
        {"extra": "not allowed"},
        {"entry_id": "missing"},
        {"api_version": 2},
    ],
)
async def test_invalid_messages_before_upstream(
    hass, dashboard_entry, hass_ws_client, changes
):
    client = await hass_ws_client(hass)
    original = dashboard_entry.runtime_data.history.async_get
    dashboard_entry.runtime_data.history.async_get = AsyncMock(wraps=original)
    kwargs = dict(series_id=1, season=2024, race_id=88001, datasets=["laps"])
    kwargs.update(changes)
    result = await call(client, dashboard_entry, "history", **kwargs)
    assert result["type"] == "result" and not result["success"]
    dashboard_entry.runtime_data.history.async_get.assert_not_awaited()


@pytest.mark.parametrize("kind", [1, 2, 3])
async def test_full_leaderboard_session_routing_and_optional_fields(
    hass, dashboard_entry, hass_ws_client, kind
):
    set_live(dashboard_entry, run_type=kind)
    client = await hass_ws_client(hass)
    result = await call(client, dashboard_entry, "live", series_id=1)
    data = result["result"]["data"]
    assert data["availability"] == "ok"
    assert (
        data["session"]["status"] == {1: "practice", 2: "qualifying", 3: "race"}[kind]
    )
    assert [d["driver_id"] for d in data["leaderboard"]] == ["99001", "99002", "99003"]
    assert data["leader_driver_id"] == "99001"
    favorite = data["leaderboard"][1]
    assert favorite["favorite"] and favorite["car_number"] == "07"
    assert favorite["position_change"]["value"] == 3
    assert data["leaderboard"][2]["last_lap_time"] is None
    assert data["scoring"]["pits"]["status"] != "available"
    assert data["scoring"]["pits"]["records"] is None
    other = await call(client, dashboard_entry, "live", series_id=2)
    assert other["result"]["data"]["leaderboard"] is None
    detail = await call(
        client,
        dashboard_entry,
        "live_driver",
        series_id=1,
        driver_id=99002,
        collection="pit_stops",
        limit=1,
    )
    assert detail["result"]["data"]["pagination"]["returned"] == 1


async def test_multiple_clients_initial_dedup_transitions_unsubscribe_disconnect(
    hass, dashboard_entry, hass_ws_client
):
    original = set_live(dashboard_entry)
    first, second = await hass_ws_client(hass), await hass_ws_client(hass)
    for client in (first, second):
        assert (await call(client, dashboard_entry, "subscribe_live", series_id=1))[
            "success"
        ]
        assert (await receive_update(client))["revision"] == 1
    dashboard_entry.runtime_data.live.async_set_updated_data(replace(original))
    await asyncio.sleep(0.13)
    for client in (first, second):
        with pytest.raises(TimeoutError):
            await client.receive_json(timeout=0.02)
    set_live(dashboard_entry, race_id=99222, run_id=99)
    for client in (first, second):
        update = await receive_update(client)
        assert update["revision"] == 2 and update["identity"]["run_id"] == "99"
    await first.send_json_auto_id({"type": "unsubscribe_events", "subscription": 1})
    assert (await first.receive_json())["success"]
    assert len(dashboard_entry.runtime_data.dashboard.subscriptions) == 1
    set_live(dashboard_entry, series_id=2)
    assert (await receive_update(second))["availability"] == "not_reported"
    await second.client.close()
    await hass.async_block_till_done()
    assert not dashboard_entry.runtime_data.dashboard.subscriptions


async def test_source_stale_failure_and_recovery_without_extra_requests(
    hass, dashboard_entry, hass_ws_client
):
    set_live(dashboard_entry)
    live = dashboard_entry.runtime_data.live
    client = await hass_ws_client(hass)
    await call(client, dashboard_entry, "subscribe_live", series_id=1)
    await receive_update(client)
    with pytest.MonkeyPatch.context() as monkeypatch:
        getter = AsyncMock(side_effect=AssertionError("No extra request permitted"))
        monkeypatch.setattr(live.provider, "async_get_live", getter)
        future = dt_util.utcnow() + timedelta(minutes=16)
        monkeypatch.setattr(dt_util, "utcnow", lambda: future)
        async_fire_time_changed(hass, future)
        update = await receive_update(client)
        assert update["availability"] == "stale" and update["leaderboard"] is None
        getter.assert_not_awaited()
    live.last_update_success = False
    live.async_update_listeners()
    assert (await receive_update(client))["availability"] == "offline"
    set_live(dashboard_entry)
    assert (await receive_update(client))["availability"] == "ok"


async def test_history_analytics_pagination_and_no_entity_mutation(
    hass, dashboard_entry, hass_ws_client
):
    registry = er.async_get(hass)
    before = {
        e.entity_id
        for e in er.async_entries_for_config_entry(registry, dashboard_entry.entry_id)
    }
    dashboard_entry.runtime_data.history.async_get = AsyncMock(
        return_value=historical(*HistoryDataset)
    )
    client = await hass_ws_client(hass)
    params = dict(
        series_id=1,
        season=2024,
        race_id=88001,
        datasets=[k.value for k in HistoryDataset],
    )
    result = await call(client, dashboard_entry, "history", limit=2, **params)
    data = result["result"]["data"]
    assert len(data["records"]) == 2 and data["pagination"]["next_offset"] == 2
    missing_token = await call(client, dashboard_entry, "history", offset=2, **params)
    assert missing_token["error"]["code"] == "snapshot_required"
    continued = await call(
        client,
        dashboard_entry,
        "history",
        offset=2,
        snapshot=data["pagination"]["snapshot"],
        **params,
    )
    assert continued["success"]
    analytics = await call(
        client,
        dashboard_entry,
        "analytics",
        driver_ids=[99002],
        first_lap=1,
        last_lap=10,
        windows=[5, 10],
        time_basis="all_available",
        **params,
    )
    assert analytics["success"]
    assert analytics["result"]["data"]["contract_version"] == 1
    json.dumps(analytics, allow_nan=False)
    assert {
        e.entity_id
        for e in er.async_entries_for_config_entry(registry, dashboard_entry.entry_id)
    } == before


@pytest.mark.parametrize("lifecycle", ["unload", "reload", "stop"])
async def test_entry_lifecycle_closes_subscriptions_and_blocked_requests(
    hass, dashboard_entry, hass_ws_client, lifecycle, monkeypatch
):
    if lifecycle == "stop":
        # HA's shutdown clock advances can re-arm aiohttp's native keepalive.
        # Disable only that transport keepalive; integration cleanup stays real.
        monkeypatch.setattr(
            "aiohttp.web_ws.WebSocketResponse._reset_heartbeat", lambda _: None
        )
    client = await hass_ws_client(hass)
    await call(client, dashboard_entry, "subscribe_live", series_id=1)
    await receive_update(client)
    runtime = dashboard_entry.runtime_data
    started, cancelled = asyncio.Event(), asyncio.Event()

    async def blocked(*_):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            cancelled.set()

    runtime.history.provider.async_get_history = AsyncMock(side_effect=blocked)
    await client.send_json_auto_id(
        message(
            dashboard_entry,
            "history",
            series_id=1,
            season=2024,
            race_id=88001,
            datasets=["laps"],
        )
    )
    await started.wait()
    if lifecycle == "stop":
        await hass.async_stop()
    elif lifecycle == "reload":
        assert await hass.config_entries.async_reload(dashboard_entry.entry_id)
    else:
        assert await hass.config_entries.async_unload(dashboard_entry.entry_id)
    if lifecycle != "stop":
        assert (await receive_update(client))["availability"] == "entry_unavailable"
    assert cancelled.is_set() and runtime.dashboard.closed
    assert not runtime.dashboard.requests and not runtime.dashboard.subscriptions
    await client.client.close()


async def test_cf_bootstrap_subscriptions_never_add_gets(
    hass, aioclient_mock, hass_ws_client
):
    entry = await cf_entry(hass, aioclient_mock)
    assert aioclient_mock.call_count == 7

    first, second = await hass_ws_client(hass), await hass_ws_client(hass)
    for client in (first, second):
        assert (await call(client, entry, "bootstrap"))["success"]
        assert (await call(client, entry, "subscribe_live", series_id=1))["success"]
        await receive_update(client)
    assert aioclient_mock.call_count == 7


async def test_unauthenticated_socket_cannot_execute_commands(
    hass, aiohttp_client, socket_enabled, monkeypatch
):
    # Keep native authentication and sockets; isolate aiohttp's rejected-auth
    # heartbeat timer from HA's test clock and shutdown acceleration.
    monkeypatch.setattr(
        "aiohttp.web_ws.WebSocketResponse._reset_heartbeat", lambda _: None
    )
    assert await async_setup_component(hass, "websocket_api", {})
    client = await aiohttp_client(hass.http.app)
    socket = await client.ws_connect("/api/websocket")
    assert (await socket.receive_json())["type"] == "auth_required"
    await socket.send_json({"type": PREFIX + "bootstrap", "id": 1})
    assert (await socket.receive_json())["type"] == "auth_invalid"
    await socket.close()
    await client.close()


async def test_invalid_token_cannot_authenticate(
    hass, aiohttp_client, socket_enabled, monkeypatch
):
    # Keep native authentication and sockets; isolate aiohttp's rejected-auth
    # heartbeat timer from HA's test clock and shutdown acceleration.
    monkeypatch.setattr(
        "aiohttp.web_ws.WebSocketResponse._reset_heartbeat", lambda _: None
    )
    assert await async_setup_component(hass, "websocket_api", {})
    client = await aiohttp_client(hass.http.app)
    socket = await client.ws_connect("/api/websocket")
    await socket.receive_json()
    await socket.send_json({"type": "auth", "access_token": "fictional-invalid"})
    assert (await socket.receive_json())["type"] == "auth_invalid"
    await socket.close()
    await client.close()


async def test_subscription_cap_coalescing_and_revoked_admin(
    hass, dashboard_entry, hass_ws_client, hass_admin_user
):
    set_live(dashboard_entry)
    client = await hass_ws_client(hass)
    for _ in range(4):
        assert (await call(client, dashboard_entry, "subscribe_live", series_id=1))[
            "success"
        ]
        await receive_update(client)
    assert (await call(client, dashboard_entry, "subscribe_live", series_id=1))[
        "error"
    ]["code"] == "subscription_limit"
    original = dashboard_entry.runtime_data.live.data
    for lap in range(50, 150):
        dashboard_entry.runtime_data.live.async_set_updated_data(
            replace(original, lap=lap)
        )
    for _ in range(4):
        data = await receive_update(client)
        assert data["revision"] == 2 and data["session"]["lap"] == 149
    hass_admin_user.groups = []
    dashboard_entry.runtime_data.live.async_update_listeners()
    for _ in range(4):
        assert (await client.receive_json())["error"]["code"] == "unauthorized"
    assert not dashboard_entry.runtime_data.dashboard.subscriptions


async def test_rate_limit_is_shared_across_same_users_tabs(
    hass, dashboard_entry, hass_ws_client, monkeypatch
):
    first, second = await hass_ws_client(hass), await hass_ws_client(hass)
    for index in range(30):
        assert (
            await call(first if index % 2 else second, dashboard_entry, "bootstrap")
        )["success"]
    assert (await call(first, dashboard_entry, "bootstrap"))["error"][
        "code"
    ] == "rate_limited"
    now = dashboard.monotonic()
    monkeypatch.setattr(dashboard, "monotonic", lambda: now + 11)
    assert (await call(second, dashboard_entry, "bootstrap"))["success"]


async def test_cancelled_client_preserves_shared_history_peer_and_request_budget(
    hass, dashboard_entry, hass_ws_client
):
    first, second, third = [await hass_ws_client(hass) for _ in range(3)]
    provider = dashboard_entry.runtime_data.history.provider
    original = provider.async_get_history
    started, release, cancelled = asyncio.Event(), asyncio.Event(), asyncio.Event()

    async def blocked(*args):
        started.set()
        try:
            await release.wait()
            return await original(*args)
        finally:
            cancelled.set()

    provider.async_get_history = AsyncMock(side_effect=blocked)
    kwargs = dict(series_id=1, season=2024, race_id=88001, datasets=["laps"])
    for client in (first, second):
        command = "history" if client is first else "analytics"
        selection = (
            {}
            if client is first
            else {
                "driver_ids": [99002],
                "first_lap": 1,
                "last_lap": 10,
                "windows": [5],
                "time_basis": "all_available",
            }
        )
        await client.send_json_auto_id(
            message(dashboard_entry, command, **kwargs, **selection)
        )
    await started.wait()
    await hass.async_block_till_done()
    result = await call(third, dashboard_entry, "history", **kwargs)
    assert result["error"]["code"] == "request_limit"
    assert provider.async_get_history.await_count == 1
    await first.client.close()
    await hass.async_block_till_done()
    assert len(dashboard_entry.runtime_data.dashboard.requests) == 1
    assert not cancelled.is_set()
    release.set()
    assert (await second.receive_json())["success"]
    assert not dashboard_entry.runtime_data.dashboard.requests


@pytest.mark.parametrize(
    "changes",
    [
        {"driver_ids": [1] * 9},
        {"driver_ids": [1, 1]},
        {"driver_ids": [True]},
        {"first_lap": 10, "last_lap": 1},
        {"first_lap": 1, "last_lap": 5001},
        {"windows": [4]},
        {"time_basis": "green_flag"},
        {"entry_id": "x" * 129},
        {"driver_ids": list(range(1, 9)), "last_lap": 5000, "windows": [5, 10]},
    ],
)
async def test_analytics_limits_reject_before_history(
    hass, dashboard_entry, hass_ws_client, changes
):
    client = await hass_ws_client(hass)
    history = dashboard_entry.runtime_data.history
    history.async_get = AsyncMock(side_effect=AssertionError("No history I/O"))
    kwargs = dict(
        series_id=1,
        season=2024,
        race_id=88001,
        datasets=["laps"],
        driver_ids=[99002],
        first_lap=1,
        last_lap=10,
        windows=[5],
        time_basis="all_available",
    )
    kwargs.update(changes)
    assert not (await call(client, dashboard_entry, "analytics", **kwargs))["success"]
    history.async_get.assert_not_awaited()


async def test_cancelled_serializer_keeps_its_slot_until_worker_drains(
    hass, dashboard_entry, hass_ws_client, monkeypatch
):
    import threading

    first, second, third = [await hass_ws_client(hass) for _ in range(3)]
    started = asyncio.Event()
    release = threading.Event()
    original = dashboard.build_index

    def blocked(*args):
        hass.loop.call_soon_threadsafe(started.set)
        assert release.wait(timeout=5)
        return original(*args)

    monkeypatch.setattr(dashboard, "build_index", blocked)
    kwargs = dict(series_id=1, season=2024, race_id=88001, datasets=["laps"])
    for client in (first, second):
        await client.send_json_auto_id(message(dashboard_entry, "history", **kwargs))
    await started.wait()
    await first.client.close()
    assert len(dashboard_entry.runtime_data.dashboard.requests) == 2
    assert (await call(third, dashboard_entry, "history", **kwargs))["error"][
        "code"
    ] == "request_limit"
    release.set()
    assert (await second.receive_json())["success"]
    await hass.async_block_till_done()
    assert not dashboard_entry.runtime_data.dashboard.requests
    assert len(dashboard_entry.runtime_data.dashboard.snapshots.leases) == 1
    await second.client.close()
    await hass.async_block_till_done()
    assert not dashboard_entry.runtime_data.dashboard.snapshots.leases


async def test_entry_wide_subscription_limit_and_foreign_entry(
    hass, dashboard_entry, hass_ws_client, monkeypatch
):
    from pytest_homeassistant_custom_component.common import MockConfigEntry

    monkeypatch.setattr(dashboard, "MAX_SUBSCRIPTIONS", 1)
    first, second = await hass_ws_client(hass), await hass_ws_client(hass)
    assert (await call(first, dashboard_entry, "subscribe_live", series_id=1))[
        "success"
    ]
    await receive_update(first)
    assert (await call(second, dashboard_entry, "subscribe_live", series_id=2))[
        "error"
    ]["code"] == "subscription_limit"
    foreign = MockConfigEntry(domain="input_boolean")
    foreign.add_to_hass(hass)
    assert (await call(second, foreign, "bootstrap"))["error"][
        "code"
    ] == "entry_unavailable"


async def test_bootstrap_sorts_first_future_activity_and_preserves_ambiguous_time(
    hass, dashboard_entry, hass_ws_client
):
    from custom_components.nascar_race_center.models import Race, Session

    now = dt_util.utcnow()
    race = Race(
        1,
        88001,
        "Unknown race instant",
        season=2026,
        sessions=(
            Session("early", "Practice", "practice", now + timedelta(hours=1)),
            Session("late", "Race", "race", now + timedelta(hours=20)),
        ),
    )
    later = Race(1, 88002, "Later activity", now + timedelta(hours=2), season=2026)
    cancelled = Race(
        1,
        88003,
        "Only canceled time",
        season=2026,
        sessions=(
            Session(
                "cancel",
                "Canceled",
                "practice",
                now + timedelta(minutes=10),
                status="canceled",
            ),
        ),
    )
    coordinator = dashboard_entry.runtime_data.schedule
    coordinator.async_set_updated_data(
        replace(coordinator.data, races={1: (later, cancelled, race)})
    )
    client = await hass_ws_client(hass)
    data = (await call(client, dashboard_entry, "bootstrap"))["result"]["data"]
    assert [r["race_id"] for r in data["upcoming"]] == ["88001", "88002"]
    assert data["upcoming"][0]["start_time"] is None
    assert data["upcoming"][0]["sessions"][0]["session_id"] == "early"
    assert data["next_activity"]["session"]["session_id"] == "early"
