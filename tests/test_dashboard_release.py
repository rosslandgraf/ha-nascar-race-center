"""Snapshot release journeys on authenticated HA sockets; no NASCAR traffic."""

import asyncio
import threading

import pytest
from test_dashboard_websocket import call, message
from test_init import demo_entry

from custom_components.nascar_race_center import dashboard, dashboard_snapshots


async def setup(hass):
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    return entry


def selection(index=0, analytics=False):
    params = dict(
        series_id=1,
        season=2026,
        race_id=202601 + index,
        datasets=["weekend", "laps"],
        limit=1,
    )
    if analytics:
        params.update(
            driver_ids=[99002],
            first_lap=1,
            last_lap=10,
            windows=[5],
            time_basis="all_available",
        )
    return params


async def test_twenty_selections_release_abandoned_keep_active(
    hass, hass_ws_client, monkeypatch
):
    entry = await setup(hass)
    client = await hass_ws_client(hass)
    clock = [dashboard.monotonic()]
    monkeypatch.setattr(dashboard, "monotonic", lambda: clock[0])
    active = (await call(client, entry, "history", **selection()))["result"]["data"]
    active_token = active["pagination"]["snapshot"]
    store = entry.runtime_data.dashboard.snapshots
    peak_bytes = 0
    for index in range(1, 21):
        clock[0] += 0.4  # The card's paced requests respect the unchanged 30/10s.
        analytics = bool(index % 2)
        result = await call(
            client,
            entry,
            "analytics" if analytics else "history",
            **selection(index, analytics),
        )
        assert result["success"], result
        token = result["result"]["data"]["pagination"]["snapshot"]
        assert len(store.leases) == 2
        peak_bytes = max(
            peak_bytes,
            sum(lease.index.retained_bytes for lease in store.leases.values()),
        )
        clock[0] += 0.4
        assert (await call(client, entry, "release_snapshot", snapshot=token))[
            "success"
        ]
        assert set(store.leases) == {active_token}
    assert peak_bytes < 2 * dashboard_snapshots.MAX_SNAPSHOT_BYTES
    # The other card's active selection still pages with the original identity.
    clock[0] += 0.4
    continued = await call(
        client, entry, "history", **selection(), snapshot=active_token, offset=1
    )
    assert continued["success"]
    assert continued["result"]["data"]["pagination"]["snapshot"] == active_token
    await client.close()
    await hass.async_block_till_done()
    assert not store.leases


@pytest.mark.parametrize("scope", ["connection", "user", "entry", "revoked"])
async def test_release_is_idempotent_and_cannot_retire_foreign_tokens(
    hass, hass_ws_client, hass_admin_user, scope
):
    entry = await setup(hass)
    client = await hass_ws_client(hass)
    original = (await call(client, entry, "history", **selection()))["result"]["data"]
    token = original["pagination"]["snapshot"]
    store = entry.runtime_data.dashboard.snapshots
    other_entry = entry
    if scope == "entry":
        other_entry = await setup(hass)
    if scope == "user":
        from homeassistant.auth.models import GROUP_ID_ADMIN

        user = await hass.auth.async_create_user(
            "Other admin", group_ids=[GROUP_ID_ADMIN]
        )
        refresh = await hass.auth.async_create_refresh_token(
            user, client_id="http://localhost/"
        )
        other = await hass_ws_client(
            hass, access_token=hass.auth.async_create_access_token(refresh)
        )
    else:
        other = await hass_ws_client(hass)
    if scope == "revoked":
        groups = hass_admin_user.groups
        hass_admin_user.groups = []
    result = await call(other, other_entry, "release_snapshot", snapshot=token)
    assert (
        result["success"]
        if scope != "revoked"
        else result["error"]["code"] == "unauthorized"
    )
    assert token in store.leases and not store.leases[token].retired
    if scope == "revoked":
        hass_admin_user.groups = groups
    assert (
        await call(client, entry, "history", **selection(), snapshot=token, offset=1)
    )["success"]
    for _ in range(2):
        assert (await call(client, entry, "release_snapshot", snapshot=token))[
            "result"
        ]["data"] == {}
    assert token not in store.leases
    assert (await call(client, entry, "history", **selection(), snapshot=token))[
        "error"
    ]["code"] == "snapshot_invalid"


async def test_release_during_reader_holds_slot_until_executor_drains(
    hass, hass_ws_client, monkeypatch
):
    entry = await setup(hass)
    client = await hass_ws_client(hass)
    first = (await call(client, entry, "history", **selection()))["result"]["data"]
    token = first["pagination"]["snapshot"]
    monkeypatch.setattr(dashboard_snapshots, "MAX_SNAPSHOTS", 1)
    started, unblock = asyncio.Event(), threading.Event()
    original = dashboard_snapshots.SnapshotIndex.page

    def blocked(*args):
        hass.loop.call_soon_threadsafe(started.set)
        assert unblock.wait(timeout=5)
        return original(*args)

    monkeypatch.setattr(dashboard_snapshots.SnapshotIndex, "page", blocked)
    await client.send_json_auto_id(
        message(entry, "history", **selection(), snapshot=token, offset=1)
    )
    await started.wait()
    store = entry.runtime_data.dashboard.snapshots
    try:
        assert (await call(client, entry, "release_snapshot", snapshot=token))[
            "success"
        ]
        assert store.leases[token].retired
        assert store.leases[token].readers == 1
        assert store.leases[token].index is not None
        peer = await hass_ws_client(hass)
        assert (await call(peer, entry, "history", **selection(1)))["error"][
            "code"
        ] == "snapshot_limit"
    finally:
        unblock.set()
    response = await client.receive_json()
    assert response["success"]
    await hass.async_block_till_done()
    assert not store.leases
    assert (await call(client, entry, "history", **selection(2)))["success"]


@pytest.mark.parametrize("collection", ["pits", "stages", "points"])
async def test_demo_no_session_live_details_have_consistent_empty_identity(
    hass, hass_ws_client, collection
):
    entry = await setup(hass)
    client = await hass_ws_client(hass)
    live = (await call(client, entry, "live", series_id=1))["result"]["data"]
    detail = (
        await call(client, entry, "live_scoring", series_id=1, collection=collection)
    )["result"]["data"]
    assert live["availability"] == "no_active_session"
    assert detail["identity"]["series_id"] == live["identity"]["series_id"]
    assert detail["identity"]["race_id"] is None
    assert detail["identity"]["run_id"] is None
    assert detail["records"] == []
