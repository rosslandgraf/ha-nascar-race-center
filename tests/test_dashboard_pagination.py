"""HA WebSocket → history broker → shared CF HTTP regression, offline only."""

import asyncio
import json

import pytest
from test_dashboard_websocket import call
from test_history import KEY, fixture
from test_phase3b_setup import cf_entry

from custom_components.nascar_race_center.dashboard_pages import history_records
from custom_components.nascar_race_center.endpoints import BASE_URL, historical_path
from custom_components.nascar_race_center.history_models import HistoryDataset


@pytest.mark.parametrize("count", [3, 7])
async def test_cf_every_page(hass, aioclient_mock, hass_ws_client, count):
    entry = await cf_entry(hass, aioclient_mock)
    kinds = tuple(HistoryDataset)[:count]
    for kind in kinds:
        aioclient_mock.get(BASE_URL + historical_path(KEY, kind), json=fixture(kind))
    client = await hass_ws_client(hass)
    params = dict(
        series_id=1,
        season=KEY.season,
        race_id=KEY.race_id,
        datasets=[k.value for k in kinds],
        limit=2,
    )
    first = await call(client, entry, "history", **params)
    assert first["success"], first
    data = first["result"]["data"]
    assert all(d["status"] == "available" for d in data["datasets"])
    assert aioclient_mock.call_count == 7 + count
    rows = list(data["records"])
    token = data["pagination"]["snapshot"]
    while data["pagination"]["next_offset"] is not None:
        result = await call(
            client,
            entry,
            "history",
            **params,
            offset=data["pagination"]["next_offset"],
            snapshot=token,
        )
        assert result["success"], result
        data = result["result"]["data"]
        rows.extend(data["records"])
        assert len(json.dumps(result).encode()) < 256 * 1024
        assert aioclient_mock.call_count == 7 + count
    # Reconstruct independently from the real parsers, preserving source order.
    from custom_components.nascar_race_center.history_models import (
        HistoryProvenance,
        HistoryResponse,
        HistoryResult,
        HistoryStatus,
    )
    from custom_components.nascar_race_center.history_parser import PARSERS

    expected = HistoryResponse(
        KEY,
        tuple(
            HistoryResult(
                HistoryStatus.AVAILABLE,
                HistoryProvenance(
                    k, KEY, "path_context_only", "unverified_context", "network"
                ),
                PARSERS[k](fixture(k), KEY),
            )
            for k in kinds
        ),
    )
    assert rows == list(history_records(expected))


def selection(**changes):
    return dict(
        series_id=1,
        season=KEY.season,
        race_id=KEY.race_id,
        datasets=["laps", "notes", "weekend"],
        limit=2,
        **changes,
    )


async def prepared(hass, aioclient_mock, *, laps=None):
    entry = await cf_entry(hass, aioclient_mock)
    for kind in HistoryDataset:
        aioclient_mock.get(
            BASE_URL + historical_path(KEY, kind),
            json=laps
            if kind == HistoryDataset.LAPS and laps is not None
            else fixture(kind),
        )
    return entry


@pytest.mark.parametrize(
    "change",
    ["modified", "datasets", "race", "expired", "tab", "user", "entry", "revoked"],
)
async def test_cursor_scope_and_expiry(
    hass, aioclient_mock, hass_ws_client, hass_admin_user, hass_access_token, change
):
    entry = await prepared(hass, aioclient_mock)
    client = await hass_ws_client(hass)
    first = await call(client, entry, "history", **selection())
    token = first["result"]["data"]["pagination"]["snapshot"]
    store = entry.runtime_data.dashboard.snapshots
    params = selection()
    params.update(snapshot=token, offset=2)
    if change == "modified":
        params["snapshot"] = ("0" if token[0] != "0" else "1") + token[1:]
    elif change == "datasets":
        params["datasets"] = ["laps"]
    elif change == "race":
        params["race_id"] += 1
    elif change == "expired":
        store.leases[token].expires = store.loop.time() - 1
    elif change == "tab":
        client = await hass_ws_client(hass)
    elif change == "user":
        from homeassistant.auth.models import GROUP_ID_ADMIN

        user = await hass.auth.async_create_user(
            "Second admin", group_ids=[GROUP_ID_ADMIN]
        )
        refresh = await hass.auth.async_create_refresh_token(
            user, client_id="http://localhost/"
        )
        client = await hass_ws_client(
            hass, access_token=hass.auth.async_create_access_token(refresh)
        )
    elif change == "entry":
        entry = await cf_entry(hass, aioclient_mock)
    elif change == "revoked":
        hass_admin_user.groups = []
    before = aioclient_mock.call_count
    result = await call(client, entry, "history", **params)
    assert not result["success"], result
    assert result["error"]["code"] in (
        "snapshot_invalid",
        "snapshot_expired",
        "unauthorized",
    )
    assert aioclient_mock.call_count == before


async def test_changed_source_keeps_old_snapshot_and_new_selection_sees_change(
    hass, aioclient_mock, hass_ws_client, monkeypatch
):
    from custom_components.nascar_race_center import api

    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    entry = await prepared(hass, aioclient_mock)
    client = await hass_ws_client(hass)
    first = await call(client, entry, "history", **selection())
    original = first["result"]["data"]
    changed = fixture(HistoryDataset.LAPS)
    changed["laps"][0]["Laps"][1]["LapTime"] = 99.0
    aioclient_mock.clear_requests()
    for kind in HistoryDataset:
        aioclient_mock.get(
            BASE_URL + historical_path(KEY, kind),
            json=changed if kind == HistoryDataset.LAPS else fixture(kind),
        )
    # Simulate ordinary eviction with the same supported transport API. Respect floor.
    entry.runtime_data.provider.api.clear_history()
    clock[0] += 61
    newer = await call(client, entry, "history", **selection())
    assert newer["success"]
    new_index = entry.runtime_data.dashboard.snapshots.leases[
        newer["result"]["data"]["pagination"]["snapshot"]
    ].index
    assert any(
        json.loads(row).get("value", {}).get("lap_time") == 99.0
        for row in new_index.rows
    )
    assert (
        newer["result"]["data"]["pagination"]["snapshot"]
        != original["pagination"]["snapshot"]
    )
    before = aioclient_mock.call_count
    old_rows = list(original["records"])
    data = original
    while data["pagination"]["next_offset"] is not None:
        result = await call(
            client,
            entry,
            "history",
            **selection(),
            snapshot=original["pagination"]["snapshot"],
            offset=data["pagination"]["next_offset"],
        )
        assert result["success"]
        data = result["result"]["data"]
        old_rows.extend(data["records"])
    assert any(r["kind"] == "lap" and r["value"]["lap_time"] == 30.25 for r in old_rows)
    assert not any(
        r["kind"] == "lap" and r["value"]["lap_time"] == 99.0 for r in old_rows
    )
    assert aioclient_mock.call_count == before


@pytest.mark.parametrize(
    "lifecycle", ["disconnect", "unload", "reload", "stop", "expiry"]
)
async def test_retained_cursor_cleanup(
    hass, aioclient_mock, hass_ws_client, monkeypatch, lifecycle
):
    if lifecycle == "stop":
        monkeypatch.setattr(
            "aiohttp.web_ws.WebSocketResponse._reset_heartbeat", lambda _: None
        )
    if lifecycle == "expiry":
        monkeypatch.setattr(
            "custom_components.nascar_race_center.dashboard_snapshots.SNAPSHOT_SECONDS",
            0.05,
        )
    entry = await prepared(hass, aioclient_mock)
    client = await hass_ws_client(hass)
    assert (await call(client, entry, "history", **selection()))["success"]
    runtime = entry.runtime_data.dashboard
    assert len(runtime.snapshots.leases) == 1
    if lifecycle == "disconnect":
        await client.client.close()
    elif lifecycle == "stop":
        await hass.async_stop()
    elif lifecycle == "expiry":
        await asyncio.sleep(0.06)
    else:
        assert await getattr(hass.config_entries, "async_" + lifecycle)(entry.entry_id)
    await hass.async_block_till_done()
    assert not runtime.snapshots.leases
    assert not runtime.requests
    if lifecycle == "reload":
        invalid = await call(
            client, entry, "history", **selection(), snapshot="0" * 64, offset=2
        )
        assert invalid["error"]["code"] == "snapshot_invalid"
    await client.client.close()


async def test_session_and_memory_rejection_before_token(
    hass, aioclient_mock, hass_ws_client, monkeypatch
):
    from custom_components.nascar_race_center import dashboard_snapshots as snapshots

    entry = await prepared(hass, aioclient_mock)
    client = await hass_ws_client(hass)
    monkeypatch.setattr(snapshots, "MAX_SNAPSHOT_BYTES", 1024)
    before = aioclient_mock.call_count
    result = await call(client, entry, "history", **selection())
    assert result["error"]["code"] == "snapshot_too_large"
    assert not entry.runtime_data.dashboard.snapshots.leases
    assert aioclient_mock.call_count == before + 3
    monkeypatch.setattr(snapshots, "MAX_SNAPSHOT_BYTES", 24 * 1024 * 1024)
    # Small single-dataset reads stay in the existing two-document HTTP cache.
    params = selection()
    params["datasets"] = ["weekend"]
    for _ in range(2):
        assert (await call(client, entry, "history", **params))["success"]
    before = aioclient_mock.call_count
    rejected = await call(client, entry, "history", **params)
    assert rejected["error"]["code"] == "snapshot_limit"
    assert aioclient_mock.call_count == before


@pytest.mark.parametrize("command", ["history", "analytics"])
async def test_large_cf_stream_all_pages_and_index_budget(
    hass, aioclient_mock, hass_ws_client, monkeypatch, command
):
    import time
    from hashlib import sha256

    from custom_components.nascar_race_center import dashboard
    from custom_components.nascar_race_center.dashboard_snapshots import (
        MAX_SNAPSHOT_BYTES,
    )

    drivers, laps = (10, 5000) if command == "history" else (8, 1250)
    payload = {
        "laps": [
            {
                "NASCARDriverID": i + 1,
                "Laps": [
                    {"Lap": n, "LapTime": 30.0 + n % 7} for n in range(1, laps + 1)
                ],
            }
            for i in range(drivers)
        ],
        "flags": [],
    }
    if command == "analytics":
        for driver in payload["laps"]:
            for row in driver["Laps"]:
                row["RunningPos"] = driver["NASCARDriverID"]
    assert len(json.dumps(payload).encode()) < 2 * 1024 * 1024
    entry = await prepared(hass, aioclient_mock, laps=payload)
    client = await hass_ws_client(hass)
    params = selection()
    params.update(datasets=[k.value for k in HistoryDataset], limit=200)
    if command == "analytics":
        params.update(
            driver_ids=list(range(1, 9)),
            first_lap=1,
            last_lap=1250,
            windows=[5, 10, 15, 20, 25, 30],
            time_basis="all_available",
        )
    start = time.perf_counter()
    first = await call(client, entry, command, **params)
    first_seconds = time.perf_counter() - start
    assert first["success"], first
    data = first["result"]["data"]
    token = data["pagination"]["snapshot"]
    lease = entry.runtime_data.dashboard.snapshots.leases[token]
    assert lease.index.retained_bytes <= MAX_SNAPSHOT_BYTES
    total = data["pagination"]["total"]
    assert total >= (50_000 if command == "history" else 79_000)
    expected_digest = sha256()
    for row in lease.index.rows:
        expected_digest.update(row)
    actual_digest = sha256()
    returned = 0
    durations = []
    before = aioclient_mock.call_count
    assert before == 14
    clock = [dashboard.monotonic()]
    monkeypatch.setattr(dashboard, "monotonic", lambda: clock[0])
    max_bytes = 0
    while True:
        for row in data["records"]:
            actual_digest.update(
                json.dumps(row, ensure_ascii=True, allow_nan=False).encode()
            )
        returned += len(data["records"])
        if data["pagination"]["next_offset"] is None:
            break
        # Preserve 30/10s rate limiting: simulate a compliant consumer's clock.
        clock[0] += 0.35
        start = time.perf_counter()
        output = await call(
            client,
            entry,
            command,
            **params,
            snapshot=token,
            offset=data["pagination"]["next_offset"],
        )
        durations.append(time.perf_counter() - start)
        assert output["success"], output
        max_bytes = max(max_bytes, len(json.dumps(output).encode()))
        assert max_bytes < 256 * 1024
        data = output["result"]["data"]
    assert returned == total
    assert actual_digest.digest() == expected_digest.digest()
    assert aioclient_mock.call_count == before
    print(
        "CF_CURSOR_MEASUREMENTS="
        + json.dumps(
            dict(
                command=command,
                records=returned,
                first_seconds=first_seconds,
                next_mean_seconds=sum(durations) / len(durations),
                next_max_seconds=max(durations),
                retained_bytes=lease.index.retained_bytes,
                max_response_bytes=max_bytes,
                continuation_gets=aioclient_mock.call_count - before,
            )
        )
    )
    await client.client.close()
    await hass.async_block_till_done()
    assert not entry.runtime_data.dashboard.snapshots.leases


async def test_global_snapshot_budget_across_entries(
    hass, aioclient_mock, hass_ws_client, monkeypatch
):
    from custom_components.nascar_race_center import dashboard_snapshots as snapshots

    monkeypatch.setattr(snapshots, "MAX_SNAPSHOTS", 2)
    monkeypatch.setattr(snapshots, "MAX_USER_SNAPSHOTS", 10)
    first = await prepared(hass, aioclient_mock)
    second = await cf_entry(hass, aioclient_mock)
    client = await hass_ws_client(hass)
    params = selection()
    params["datasets"] = ["laps"]
    assert (await call(client, first, "history", **params))["success"]
    assert (await call(client, second, "history", **params))["success"]
    assert (
        first.runtime_data.dashboard.snapshots
        is second.runtime_data.dashboard.snapshots
    )
    before = aioclient_mock.call_count
    assert (await call(client, first, "history", **params))["error"][
        "code"
    ] == "snapshot_limit"
    assert aioclient_mock.call_count == before
    await hass.config_entries.async_unload(first.entry_id)
    assert len(second.runtime_data.dashboard.snapshots.leases) == 1
    assert (await call(client, second, "history", **params))["success"]


@pytest.mark.parametrize("violation", ["row", "count"])
async def test_later_unpageable_records_reject_initial_token(
    hass, aioclient_mock, hass_ws_client, monkeypatch, violation
):
    from custom_components.nascar_race_center import dashboard_snapshots as snapshots

    entry = await prepared(hass, aioclient_mock)
    client = await hass_ws_client(hass)
    if violation == "row":
        original = snapshots.result_records

        def records(result):
            header, rows, context = original(result)
            return header, iter([*rows, {"value": "x" * (256 * 1024)}]), context

        monkeypatch.setattr(snapshots, "result_records", records)
    else:
        monkeypatch.setattr(snapshots, "MAX_SNAPSHOT_RECORDS", 3)
    result = await call(client, entry, "history", **selection())
    assert result["error"]["code"] == (
        "record_too_large" if violation == "row" else "snapshot_too_large"
    )
    assert not entry.runtime_data.dashboard.snapshots.leases


@pytest.mark.parametrize(
    "changes",
    [
        {"driver_ids": [99003]},
        {"windows": [10]},
        {"last_lap": 20},
        {"time_basis": "overlapping_valid_laps"},
    ],
)
async def test_analytics_cursor_binds_all_query_options(
    hass, aioclient_mock, hass_ws_client, changes
):
    entry = await prepared(hass, aioclient_mock)
    client = await hass_ws_client(hass)
    params = selection()
    params.update(
        driver_ids=[99002],
        first_lap=1,
        last_lap=10,
        windows=[5],
        time_basis="all_available",
    )
    first = await call(client, entry, "analytics", **params)
    assert first["success"]
    token = first["result"]["data"]["pagination"]["snapshot"]
    before = aioclient_mock.call_count
    params.update(changes)
    result = await call(client, entry, "analytics", **params, snapshot=token, offset=2)
    assert result["error"]["code"] == "snapshot_invalid"
    assert aioclient_mock.call_count == before


async def test_cursor_replay_and_page_size_change(hass, aioclient_mock, hass_ws_client):
    entry = await prepared(hass, aioclient_mock)
    client = await hass_ws_client(hass)
    first = await call(client, entry, "history", **selection())
    data = first["result"]["data"]
    params = selection()
    params.update(limit=1, snapshot=data["pagination"]["snapshot"])
    replay = await call(client, entry, "history", **params)
    assert replay["result"]["data"]["records"] == data["records"][:1]
    second = await call(client, entry, "history", **params, offset=1)
    assert second["result"]["data"]["records"] == data["records"][1:]
    assert aioclient_mock.call_count == 10


@pytest.mark.parametrize("phase", ["initial", "continuation"])
async def test_disconnected_page_worker_retains_global_slot_until_drained(
    hass, aioclient_mock, hass_ws_client, monkeypatch, phase
):
    import threading

    from test_dashboard_websocket import message

    from custom_components.nascar_race_center import dashboard_snapshots as snapshots

    monkeypatch.setattr(snapshots, "MAX_SNAPSHOTS", 1)
    entry = await prepared(hass, aioclient_mock)
    first, second = await hass_ws_client(hass), await hass_ws_client(hass)
    paging = {}
    if phase == "continuation":
        result = await call(first, entry, "history", **selection())
        token = result["result"]["data"]["pagination"]["snapshot"]
        paging = {"snapshot": token, "offset": 2}
    started, release = asyncio.Event(), threading.Event()
    original = snapshots.SnapshotIndex.page

    def blocked(*args):
        hass.loop.call_soon_threadsafe(started.set)
        assert release.wait(timeout=5)
        return original(*args)

    monkeypatch.setattr(snapshots.SnapshotIndex, "page", blocked)
    await first.send_json_auto_id(message(entry, "history", **selection(), **paging))
    await started.wait()
    try:
        await first.client.close()
        store = entry.runtime_data.dashboard.snapshots
        assert len(store.leases) == 1
        assert next(iter(store.leases.values())).retired
        result = await call(second, entry, "history", **selection())
        assert result["error"]["code"] == "snapshot_limit"
    finally:
        release.set()
    await asyncio.gather(*entry.runtime_data.dashboard.requests, return_exceptions=True)
    assert not store.leases
