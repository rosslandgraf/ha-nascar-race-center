"""Fictional observed-shape history tests; no NASCAR network traffic."""

import asyncio
import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from aiohttp import ClientConnectionError
from test_api import Response, client_with

from custom_components.nascar_race_center import api
from custom_components.nascar_race_center.endpoints import (
    LIVE_FEED,
    historical_path,
    is_historical_path,
)
from custom_components.nascar_race_center.history import MAX_IN_FLIGHT, HistoryService
from custom_components.nascar_race_center.history_models import (
    HistoricalRaceKey,
    HistoryResponse,
)
from custom_components.nascar_race_center.history_models import (
    HistoryDataset as Kind,
)
from custom_components.nascar_race_center.history_models import (
    HistoryStatus as Status,
)
from custom_components.nascar_race_center.history_parser import (
    MAX_LAP_ROWS,
    MAX_LAPS,
    MAX_NOTES,
    PARSERS,
)
from custom_components.nascar_race_center.history_provider import (
    CFHistoryProvider,
    DemoHistoryProvider,
)

KEY = HistoricalRaceKey(2024, 1, 88001)


def fixture(kind):
    return json.loads(
        (Path(__file__).parent / "fixtures" / "phase4a" / f"{kind}.json").read_text()
    )


def contextualize(value, key):
    """Explicit synthetic mutations, never a production context repair."""
    if isinstance(value, dict):
        for field, expected in (
            ("race_id", key.race_id),
            ("series_id", key.series_id),
            ("race_season", key.season),
        ):
            if field in value:
                value[field] = expected
        for child in value.values():
            contextualize(child, key)
    elif isinstance(value, list):
        for child in value:
            contextualize(child, key)
    return value


@pytest.mark.parametrize("year", [2019, 2024, 2026])
@pytest.mark.parametrize("series", [1, 2, 3])
@pytest.mark.parametrize("kind", list(Kind))
async def test_all_profiles_across_explicit_contexts(year, series, kind):
    key = HistoricalRaceKey(year, series, KEY.race_id)
    payload = contextualize(fixture(kind), key)
    client, session = client_with(Response(body=json.dumps(payload).encode()))
    result = await CFHistoryProvider(client).async_get_history(key, kind)
    assert result.status == Status.AVAILABLE
    assert result.provenance.requested == key
    assert result.provenance.coverage == "unverified_context"
    assert session.get.call_args.args[0].endswith(historical_path(key, kind))
    assert result.classification == "reported_unverified_finality"


def test_reported_fields_namespaces_and_immutable_results():
    data = PARSERS[Kind.WEEKEND](fixture(Kind.WEEKEND), KEY)
    weekend = data.weekend
    assert weekend.key == KEY
    assert weekend.timing_run_id == 10
    assert weekend.sessions[0].weekend_run_id == 77001
    assert weekend.sessions[0].timing_run_id == 6
    assert weekend.sessions[0].results[0].results_run_id == 77001
    assert weekend.sessions[0].run_type_code == 71
    assert weekend.sessions[0].run_date_utc == "2024-03-01T12:00:00"
    assert weekend.results[0].driver.car_number == "007"
    assert weekend.results[0].official_car_number == "7"
    assert weekend.results[0].points_earned == 40
    assert weekend.results[0].playoff_points_earned == 0
    assert weekend.cautions[0].flag_code == 91
    assert weekend.leaders[0].car_number == "007"
    assert weekend.stages[0].results[0].points == 10
    assert weekend.inspection_complete is True
    with pytest.raises(FrozenInstanceError):
        weekend.timing_run_id = 77001


def test_missing_results_remain_unknown_and_empty_results_remain_empty():
    payload = fixture(Kind.WEEKEND)
    del payload["weekend_race"][0]["results"]
    assert PARSERS[Kind.WEEKEND](payload, KEY).weekend.results is None
    payload["weekend_race"][0]["results"] = []
    assert PARSERS[Kind.WEEKEND](payload, KEY).weekend.results == ()


def test_lap_zero_nulls_unknown_flags_and_uninterpreted_notes():
    data = PARSERS[Kind.LAPS](fixture(Kind.LAPS), KEY)
    assert data.laps[0].driver.nascar_driver_id == 99002
    assert data.laps[0].laps[0].lap_time is None
    assert data.laps[0].laps[0].lap_speed is None
    assert data.laps[0].laps[0].running_position == 0
    assert data.laps[0].laps[1].lap_speed == 140.5
    assert data.flags[0].flag_code == 91
    notes = PARSERS[Kind.NOTES](fixture(Kind.NOTES), KEY).notes
    assert notes[0].reported_driver_ids == (99002, 99002)
    assert notes[1].reported_driver_ids == ()


def test_sentinels_loop_values_and_archived_scoring_are_not_analytics():
    averages = PARSERS[Kind.AVERAGES](fixture(Kind.AVERAGES), KEY).averages
    metrics = {m.field: m for m in averages[0].drivers[0].metrics}
    assert metrics["Con10Lap"].value == 999
    assert metrics["Con10Lap"].interpretation == "candidate_sentinel"
    assert metrics["Con10LapRank"].value is None
    assert metrics["Con30Lap"].interpretation == "missing"
    pits = PARSERS[Kind.PITS](fixture(Kind.PITS), KEY).pits
    assert pits[0].nascar_driver_id is None
    assert pits[0].activity.stop_duration is None
    assert pits[0].activity.stop.position_change == -1
    assert any(
        m.value == -1 and m.interpretation == "candidate_sentinel"
        for m in pits[0].reported_numbers
    )
    loops = PARSERS[Kind.LOOP](fixture(Kind.LOOP), KEY).loops
    assert {m.field: m.value for m in loops[0].drivers[0].metrics}["passing_diff"] == -2
    stages = PARSERS[Kind.STAGES](fixture(Kind.STAGES), KEY).stages
    assert stages[0].context.run_namespace == "stage_run"
    assert stages[0].results[0].points == 0


@pytest.mark.parametrize("kind", list(Kind))
@pytest.mark.parametrize(
    "field,value", [("race_id", 88002), ("series_id", 2), ("race_season", 2025)]
)
async def test_conflicting_context_never_repaired(kind, field, value):
    payload = fixture(kind)
    row = (
        payload["weekend_race"][0]
        if kind == Kind.WEEKEND
        else payload[0]
        if isinstance(payload, list)
        else payload
    )
    row[field] = value
    client, _ = client_with(Response(body=json.dumps(payload).encode()))
    result = await CFHistoryProvider(client).async_get_history(KEY, kind)
    assert result.status == Status.INVALID
    assert result.data is None
    assert not client._history_cache


@pytest.mark.parametrize("kind", [Kind.WEEKEND, Kind.LOOP, Kind.STAGES])
def test_nested_identity_conflicts(kind):
    payload = fixture(kind)
    row = (
        payload["weekend_race"][0]["results"][0] if kind == Kind.WEEKEND else payload[0]
    )
    row["race_id"] = 99999
    with pytest.raises(ValueError):
        PARSERS[kind](payload, KEY)


@pytest.mark.parametrize("value", [True, "99002", 0, -1, None, 1.5, 10**30])
@pytest.mark.parametrize("kind", [Kind.LAPS, Kind.WEEKEND, Kind.LOOP, Kind.STAGES])
def test_driver_namespace_is_required_and_strict(kind, value):
    payload = fixture(kind)
    if kind == Kind.LAPS:
        row, field = payload["laps"][0], "NASCARDriverID"
    elif kind == Kind.WEEKEND:
        row, field = payload["weekend_race"][0]["results"][0], "driver_id"
    elif kind == Kind.LOOP:
        row, field = payload[0]["drivers"][0], "driver_id"
    else:
        row, field = payload[0]["results"][0], "driver_id"
    row[field] = value
    row.update(
        Driver_ID="99002",
        membership_id=99002,
        driver_name="Same Name",
        car_number="007",
    )
    with pytest.raises(ValueError):
        PARSERS[kind](payload, KEY)


@pytest.mark.parametrize(
    "value", [True, "oops", float("nan"), float("inf"), -2, 10**100]
)
def test_invalid_numeric_values_do_not_become_missing(value):
    payload = fixture(Kind.LAPS)
    payload["laps"][0]["Laps"][1]["LapTime"] = value
    with pytest.raises(ValueError):
        PARSERS[Kind.LAPS](payload, KEY)


@pytest.mark.parametrize(
    "kind,payload",
    [
        (Kind.WEEKEND, []),
        (Kind.LAPS, []),
        (Kind.NOTES, {"laps": []}),
        (Kind.LOOP, {}),
        (Kind.AVERAGES, [{"NASCARDriverID": 99002}]),
        (Kind.PITS, {}),
        (Kind.STAGES, {}),
    ],
)
def test_incorrect_envelopes_are_rejected(kind, payload):
    with pytest.raises(ValueError):
        PARSERS[kind](payload, KEY)


def test_large_arrays_fail_explicitly_instead_of_truncating():
    payload = fixture(Kind.LAPS)
    payload["laps"][0]["Laps"] = [{"Lap": n} for n in range(MAX_LAPS + 1)]
    with pytest.raises(ValueError):
        PARSERS[Kind.LAPS](payload, KEY)
    payload["laps"] = [
        {"NASCARDriverID": n + 1, "Laps": [{"Lap": lap} for lap in range(MAX_LAPS)]}
        for n in range(MAX_LAP_ROWS // MAX_LAPS + 1)
    ]
    with pytest.raises(ValueError, match="budget"):
        PARSERS[Kind.LAPS](payload, KEY)
    notes = fixture(Kind.NOTES)
    notes["laps"]["0"] *= MAX_NOTES + 1
    with pytest.raises(ValueError):
        PARSERS[Kind.NOTES](notes, KEY)


@pytest.mark.parametrize("kind", list(Kind))
async def test_available_empty_is_distinct_from_missing(kind):
    payload = (
        {"weekend_race": [], "weekend_runs": []}
        if kind == Kind.WEEKEND
        else {"laps": [], "flags": []}
        if kind == Kind.LAPS
        else {"laps": {}}
        if kind == Kind.NOTES
        else []
    )
    client, _ = client_with(Response(body=json.dumps(payload).encode()))
    result = await CFHistoryProvider(client).async_get_history(KEY, kind)
    assert result.status == Status.EMPTY
    assert result.data.empty


@pytest.mark.parametrize(
    "status,expected",
    [
        (403, Status.NETWORK_ERROR),
        (429, Status.NETWORK_ERROR),
        (503, Status.NETWORK_ERROR),
        (404, Status.UNVERIFIED),
        (410, Status.UNVERIFIED),
    ],
)
async def test_http_failures_and_retry_hints(status, expected):
    client, session = client_with(
        Response(status, body=b"PRIVATE RAW BODY", headers={"Retry-After": "600"})
    )
    provider = CFHistoryProvider(client)
    first = await provider.async_get_history(KEY, Kind.LAPS)
    second = await provider.async_get_history(KEY, Kind.LAPS)
    assert first.status == second.status == expected
    assert (
        first.provenance.retry_after >= 600
        if status != 404 and status != 410
        else first.provenance.retry_after > 0
    )
    assert session.get.call_count == 1
    assert "PRIVATE" not in repr((first, client.diagnostics()))


async def test_partial_availability_preserves_independently_valid_data():
    client, session = client_with(
        Response(body=json.dumps(fixture(Kind.WEEKEND)).encode()), Response(403)
    )
    service = HistoryService(CFHistoryProvider(client), (1, 2, 3))
    result = await service.async_get(KEY, (Kind.WEEKEND, Kind.LAPS))
    assert result.status == Status.PARTIAL
    assert (
        result.dataset(Kind.WEEKEND).data.weekend.results[0].driver.nascar_driver_id
        == 99002
    )
    assert result.dataset(Kind.LAPS).status == Status.NETWORK_ERROR
    assert session.get.call_count == 2
    await service.async_close()


async def test_cache_expiry_and_304_report_delivery(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    client, session = client_with(
        Response(
            body=json.dumps(fixture(Kind.LAPS)).encode(), headers={"ETag": '"example"'}
        ),
        Response(304),
    )
    provider = CFHistoryProvider(client)
    first = await provider.async_get_history(KEY, Kind.LAPS)
    cached = await provider.async_get_history(KEY, Kind.LAPS)
    assert cached.provenance.delivery == "cache"
    assert cached.provenance.response_at == first.provenance.response_at
    clock[0] += 3601
    revalidated = await provider.async_get_history(KEY, Kind.LAPS)
    assert revalidated.provenance.delivery == "revalidated"
    assert session.get.call_count == 2
    assert session.get.call_args.kwargs["headers"]["If-None-Match"] == '"example"'


@pytest.mark.parametrize("policy", ["no-cache", "no-store"])
async def test_concurrent_consumers_share_one_result_even_without_fresh_cache(policy):
    client, session = client_with(
        Response(
            body=json.dumps(fixture(Kind.LAPS)).encode(),
            headers={"Cache-Control": policy},
        )
    )
    service = HistoryService(CFHistoryProvider(client), (1,))
    responses = await asyncio.gather(
        *(service.async_get(KEY, (Kind.LAPS,)) for _ in range(30))
    )
    assert all(r.status == Status.AVAILABLE for r in responses)
    assert session.get.call_count == 1
    assert not service._flights
    if policy == "no-store":
        assert not client._history_cache


async def test_same_race_id_never_collides_across_years_and_series():
    client, session = client_with(
        *(Response(body=b'{"laps":[],"flags":[]}') for _ in range(4))
    )
    provider = CFHistoryProvider(client)
    keys = [
        KEY,
        replace(KEY, season=2025),
        replace(KEY, series_id=2),
        replace(KEY, series_id=3),
    ]
    for key in keys:
        result = await provider.async_get_history(key, Kind.LAPS)
        assert result.provenance.requested == key
    assert len({c.args[0] for c in session.get.call_args_list}) == 4
    assert len(client._history_cache) == 2
    assert not client._cache


async def test_history_cache_does_not_evict_live_and_is_released():
    client, _ = client_with(
        Response(body=b"{}"),
        *(Response(body=b'{"laps":[],"flags":[]}') for _ in range(4)),
    )
    await client.async_get_json(LIVE_FEED, minimum_ttl=300)
    provider = CFHistoryProvider(client)
    for race_id in range(4):
        await provider.async_get_history(replace(KEY, race_id=race_id + 1), Kind.LAPS)
    assert LIVE_FEED in client._cache
    provider.clear()
    assert not client._history_cache
    assert LIVE_FEED in client._cache


@pytest.mark.parametrize(
    "body", [b"{", b'{"laps":[],"laps":[]}', b"NaN", b" " * (2 * 1024 * 1024 + 1)]
)
async def test_invalid_or_oversize_json_is_bounded(body):
    client, _ = client_with(Response(body=body))
    result = await CFHistoryProvider(client).async_get_history(KEY, Kind.LAPS)
    assert result.status == Status.INVALID
    assert result.data is None


async def test_connection_failure_and_304_without_cache():
    for response, expected in (
        (ClientConnectionError("private detail"), Status.NETWORK_ERROR),
        (Response(304), Status.INVALID),
    ):
        client, _ = client_with(response)
        result = await CFHistoryProvider(client).async_get_history(KEY, Kind.LAPS)
        assert result.status == expected
        assert "private detail" not in repr(result)


@pytest.mark.parametrize(
    "key",
    [
        (True, 1, 1),
        (2024.0, 1, 1),
        (2024, True, 1),
        (2024, 1, "1"),
        (1947, 1, 1),
        (2024, 4, 1),
        (2024, 1, -1),
        (2024, 1, 10**11),
    ],
)
def test_selected_identity_validation(key):
    with pytest.raises(ValueError):
        HistoricalRaceKey(*key)


@pytest.mark.parametrize(
    "path",
    [
        "/cacher/2024/1/88001/snappytv.json",
        "/cacher/2024/1/88001/driver-recap.json",
        "/drive/1/configs-ng.json",
        "/cacher/1947/1/1/lap-times.json",
        "/cacher/2024/1/0/lap-times.json",
        "/cacher/2024/1/1/lap-times.json?token=x",
        "/cacher/2024/4/1/lap-times.json",
        "/loopstats/prod/2024/1/../1.json",
    ],
)
async def test_endpoint_allowlist_rejects_speculation_and_path_injection(path):
    client, session = client_with()
    assert not is_historical_path(path)
    with pytest.raises(ValueError):
        await client.async_get_json(path)
    session.get.assert_not_called()


async def test_selection_requires_explicit_allowlisted_datasets_and_monitored_series():
    service = HistoryService(DemoHistoryProvider(), (1,))
    for key, kinds in (
        (replace(KEY, series_id=2), (Kind.LAPS,)),
        (KEY, ()),
        (KEY, ("laps",)),
        (KEY, (Kind.LAPS, Kind.LAPS)),
    ):
        with pytest.raises(ValueError):
            await service.async_get(key, kinds)


async def test_cancellation_of_one_consumer_preserves_other_and_last_aborts():
    provider = DemoHistoryProvider()
    started, release, cancelled = asyncio.Event(), asyncio.Event(), asyncio.Event()
    original = provider.async_get_history

    async def blocked(*args):
        started.set()
        try:
            await release.wait()
            return await original(*args)
        finally:
            cancelled.set()

    provider.async_get_history = AsyncMock(side_effect=blocked)
    service = HistoryService(provider, (1,))
    first = asyncio.create_task(service.async_get(KEY, (Kind.WEEKEND,)))
    second = asyncio.create_task(service.async_get(KEY, (Kind.WEEKEND,)))
    await started.wait()
    first.cancel()
    with pytest.raises(asyncio.CancelledError):
        await first
    assert not cancelled.is_set()
    release.set()
    assert (await second).status == Status.AVAILABLE
    assert provider.async_get_history.await_count == 1
    release.clear()
    started.clear()
    cancelled.clear()
    last = asyncio.create_task(service.async_get(KEY, (Kind.LAPS,)))
    await started.wait()
    last.cancel()
    with pytest.raises(asyncio.CancelledError):
        await last
    assert cancelled.is_set()
    assert not service._flights


async def test_unique_inflight_budget_and_shutdown_are_bounded():
    provider = DemoHistoryProvider()
    ready = asyncio.Event()
    provider.async_get_history = AsyncMock(side_effect=lambda *_: None)

    async def blocked(*_):
        if provider.async_get_history.await_count == MAX_IN_FLIGHT:
            ready.set()
        await asyncio.Event().wait()

    provider.async_get_history.side_effect = blocked
    service = HistoryService(provider, (1,))
    tasks = [
        asyncio.create_task(
            service.async_get(replace(KEY, race_id=n + 1), (Kind.LAPS,))
        )
        for n in range(MAX_IN_FLIGHT)
    ]
    await ready.wait()
    over = await service.async_get(KEY, (Kind.LAPS,))
    assert over.results[0].reason == "request_budget"
    await service.async_close()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    assert all(isinstance(r, asyncio.CancelledError) for r in results)
    assert not service._flights
    with pytest.raises(RuntimeError):
        await service.async_get(KEY, (Kind.LAPS,))


async def test_demo_is_clearly_fictional():
    response = await HistoryService(DemoHistoryProvider(), (1, 2, 3)).async_get(
        KEY, tuple(Kind)
    )
    assert response.status == Status.AVAILABLE
    assert all(r.provenance.coverage == "fictional" for r in response.results)
    assert "Fictional" in response.dataset(Kind.WEEKEND).data.weekend.name
    invalid = replace(response.results[0], status=Status.NOT_PUBLISHED, data=None)
    assert HistoryResponse(KEY, (invalid,)).status == Status.NOT_PUBLISHED


def test_unknown_negative_enum_codes_survive_without_interpretation():
    payload = fixture(Kind.LAPS)
    payload["flags"][0]["FlagState"] = -1
    assert PARSERS[Kind.LAPS](payload, KEY).flags[0].flag_code == -1
    payload = fixture(Kind.WEEKEND)
    payload["weekend_runs"][0]["run_type"] = -1
    assert PARSERS[Kind.WEEKEND](payload, KEY).weekend.sessions[0].run_type_code == -1


async def test_success_retry_hint_and_explicit_revalidation_floor(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    client, session = client_with(
        Response(
            body=json.dumps(fixture(Kind.LAPS)).encode(),
            headers={"Cache-Control": "no-cache", "Retry-After": "600", "ETag": '"v1"'},
        ),
        Response(304),
    )
    provider = CFHistoryProvider(client)
    assert (await provider.async_get_history(KEY, Kind.LAPS)).status == Status.AVAILABLE
    clock[0] += 61
    deferred = await provider.async_get_history(KEY, Kind.LAPS)
    assert deferred.status == Status.NETWORK_ERROR
    assert deferred.provenance.retry_after >= 539
    assert session.get.call_count == 1
    clock[0] += 540
    assert (await provider.async_get_history(KEY, Kind.LAPS)).status == Status.AVAILABLE
    assert session.get.call_count == 2


async def test_history_rate_limit_blocks_other_endpoints_without_retry():
    client, session = client_with(Response(429, headers={"Retry-After": "600"}))
    result = await CFHistoryProvider(client).async_get_history(KEY, Kind.LAPS)
    assert result.status == Status.NETWORK_ERROR
    from custom_components.nascar_race_center.models import RateLimitedError

    with pytest.raises(RateLimitedError):
        await client.async_get_json(LIVE_FEED)
    assert session.get.call_count == 1


async def test_cancelling_actual_transport_read_releases_cache_and_lock():
    started, cancelled = asyncio.Event(), asyncio.Event()

    class BlockedResponse(Response):
        async def iter_chunked(self, size):
            started.set()
            try:
                await asyncio.Event().wait()
                yield b""
            finally:
                cancelled.set()

    client, _ = client_with(BlockedResponse(), Response(body=b"{}"))
    service = HistoryService(CFHistoryProvider(client), (1,))
    consumer = asyncio.create_task(service.async_get(KEY, (Kind.LAPS,)))
    await started.wait()
    consumer.cancel()
    with pytest.raises(asyncio.CancelledError):
        await consumer
    assert cancelled.is_set()
    assert not client._history_cache
    assert not client._request_lock.locked()
    assert await client.async_get_json(LIVE_FEED) == {}


@pytest.mark.parametrize(
    "kind", [Kind.LAPS, Kind.WEEKEND, Kind.LOOP, Kind.AVERAGES, Kind.STAGES]
)
def test_duplicate_driver_identity_rejected_in_each_scope(kind):
    payload = fixture(kind)
    rows = (
        payload["laps"]
        if kind == Kind.LAPS
        else payload["weekend_race"][0]["results"]
        if kind == Kind.WEEKEND
        else payload[0]["drivers"]
        if kind == Kind.LOOP
        else payload[0]["Items"]
        if kind == Kind.AVERAGES
        else payload[0]["results"]
    )
    rows.append(rows[0].copy())
    with pytest.raises(ValueError):
        PARSERS[kind](payload, KEY)
