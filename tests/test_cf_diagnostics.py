"""Trace transport, parsing and real HA rendering with offline responses only."""

import asyncio
import json

import pytest
from aiohttp import ClientConnectionError
from pytest_homeassistant_custom_component.common import MockConfigEntry
from test_api import Response, client_with
from test_cf_compatibility import fixture
from test_phase3a_sensors import state

from custom_components.nascar_race_center import api
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
from custom_components.nascar_race_center.models import ProviderError


@pytest.mark.parametrize(
    ("response", "json_status", "status"),
    [
        (Response(body=b"<html>private-body-marker</html>"), "invalid", 200),
        (Response(body=b'{"series_id":1,"series_id":2}'), "invalid", 200),
        (Response(body=b'{"value":NaN}'), "invalid", 200),
        (Response(body=b'{"value":Infinity}'), "invalid", 200),
        (Response(body=b'{"value":-Infinity}'), "invalid", 200),
        (Response(body=b" " * (2 * 1024 * 1024 + 1)), "too_large", 200),
        (Response(304), "not_checked", 304),
        (Response(403, body=b"private-body-marker"), "not_checked", 403),
        (Response(503, body=b"private-body-marker"), "not_checked", 503),
    ],
)
async def test_http_success_json_failure_and_safe_response_metadata(
    response, json_status, status
):
    client, session = client_with(response)
    with pytest.raises(ProviderError) as error:
        await client.async_get_json(LIVE_FEED)
    diagnostics = client.diagnostics()[LIVE_FEED]
    assert diagnostics["delivery"] == "network"
    assert diagnostics["transport"] == "response"
    assert diagnostics["http_status"] == status
    assert error.value.status == status
    assert diagnostics["json_status"] == json_status
    assert diagnostics["response_at"] is not None
    assert "private-body-marker" not in json.dumps(client.diagnostics())
    assert session.get.call_count == 1


async def test_cache_and_304_are_not_reported_as_new_json_bodies(monkeypatch):
    clock = [1000.0]
    monkeypatch.setattr(api, "_monotonic", lambda: clock[0])
    client, session = client_with(
        Response(
            body=b'{"sensitive":"body-marker"}', headers={"ETag": '"header-marker"'}
        ),
        Response(304),
    )
    await client.async_get_json(LIVE_FEED, minimum_ttl=60)
    first = client.diagnostics()[LIVE_FEED]
    await client.async_get_json(LIVE_FEED, minimum_ttl=60)
    assert client.diagnostics()[LIVE_FEED] == {**first, "delivery": "cache"}
    assert session.get.call_count == 1
    clock[0] += 61
    await client.async_get_json(LIVE_FEED, minimum_ttl=60)
    assert client.diagnostics()[LIVE_FEED]["delivery"] == "revalidated"
    assert client.diagnostics()[LIVE_FEED]["http_status"] == 304
    assert client.diagnostics()[LIVE_FEED]["json_status"] == "valid"
    assert session.get.call_count == 2
    assert "body-marker" not in json.dumps(client.diagnostics())
    assert "header-marker" not in json.dumps(client.diagnostics())


async def test_connection_error_and_cooldown_do_not_claim_an_http_response():
    client, session = client_with(ClientConnectionError("private-network-marker"))
    with pytest.raises(ProviderError):
        await client.async_get_json(LIVE_FEED)
    result = client.diagnostics()[LIVE_FEED]
    assert result["transport"] == "connection_error"
    assert result["http_status"] is None
    assert result["response_at"] is None
    assert result["json_status"] == "not_checked"
    with pytest.raises(ProviderError):
        await client.async_get_json(LIVE_FEED)
    assert client.diagnostics()[LIVE_FEED]["delivery"] == "cooldown"
    assert session.get.call_count == 1
    assert "private-network-marker" not in json.dumps(client.diagnostics())


async def test_cancelled_request_propagates_and_does_not_report_json():
    client, _ = client_with(asyncio.CancelledError())
    with pytest.raises(asyncio.CancelledError):
        await client.async_get_json(LIVE_FEED)
    assert client.diagnostics()[LIVE_FEED]["delivery"] == "cancelled"
    assert client.diagnostics()[LIVE_FEED]["json_status"] == "not_checked"


async def test_diagnostics_are_bounded_detached_and_reject_unapproved_paths():
    client, _ = client_with(*(Response(body=b"null") for _ in range(30)))
    for year in range(2000, 2030):
        await client.async_get_json(schedule_path(year))
    results = client.diagnostics()
    assert len(results) == 24
    assert schedule_path(2000) not in results
    results[schedule_path(2029)]["http_status"] = 999
    assert client.diagnostics()[schedule_path(2029)]["http_status"] == 200
    with pytest.raises(ValueError):
        await client.async_get_json("/unapproved/private-path")
    assert "/unapproved/private-path" not in client.diagnostics()


@pytest.mark.parametrize("live_series", [1, 2])
async def test_cf_pipeline_reaches_ha_entities_and_diagnostics_without_extra_requests(
    hass, aioclient_mock, freezer, live_series
):
    freezer.move_to("2026-10-21T12:04:30Z")
    live = fixture("live")
    live["series_id"] = live_series
    aioclient_mock.get(BASE_URL + schedule_path(2026), json=fixture("schedule"))
    for series in (1, 2, 3):
        aioclient_mock.get(BASE_URL + schedule_feed_path(2026, series), json=[])
    aioclient_mock.get(BASE_URL + DRIVERS, json=fixture("drivers"))
    aioclient_mock.get(BASE_URL + TRACKS, json=fixture("tracks"))
    aioclient_mock.get(BASE_URL + LIVE_FEED, json=live)
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PROVIDER: PROVIDER_CF,
            CONF_SERIES: ["1", "2", "3"],
            CONF_FAVORITE_DRIVERS: ["99011"],
            CONF_DATA_USE_AUTHORIZED: True,
        },
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert aioclient_mock.call_count == 7
    assert diagnostics["cf_pipeline"]["transport"][LIVE_FEED]["http_status"] == 200
    assert diagnostics["cf_pipeline"]["parsers"][LIVE_FEED] == "parsed"
    assert diagnostics["live"]["usable_timing"] == {
        str(series): series == live_series for series in (1, 2, 3)
    }
    assert diagnostics["live"]["series_health"] == {
        str(series): "ok" if series == live_series else "not_reported"
        for series in (1, 2, 3)
    }
    assert diagnostics["schedule"]["unknown_start_time_counts"] == {
        "1": 1,
        "2": 1,
        "3": 1,
    }
    assert state(hass, entry, "driver_99011_live_position").state == "1"
    assert state(hass, entry, "driver_99011_metadata").attributes["team"] is None
    assert state(hass, entry, f"{live_series}_current_stage").state == "2"
    # Cache reuse is visible; diagnostics and rendering cause no extra I/O.
    await entry.runtime_data.live.async_refresh()
    assert aioclient_mock.call_count == 7
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["cf_pipeline"]["transport"][LIVE_FEED]["delivery"] == "cache"
    assert "Synthetic Driver" not in json.dumps(diagnostics)
    assert "88021" not in json.dumps(diagnostics)
    # After cache expiry, invalid JSON preserves prior context only as last-good.
    freezer.tick(61)
    aioclient_mock.clear_requests()
    aioclient_mock.get(BASE_URL + LIVE_FEED, text="<html>private-marker</html>")
    await entry.runtime_data.live.async_refresh()
    await hass.async_block_till_done()
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["live"]["retained_last_good"]
    assert not any(diagnostics["live"]["usable_timing"].values())
    assert (
        diagnostics["cf_pipeline"]["transport"][LIVE_FEED]["json_status"] == "invalid"
    )
    assert diagnostics["cf_pipeline"]["parsers"][LIVE_FEED] == "not_parsed"
    assert state(hass, entry, "driver_99011_live_position").state == "unavailable"
    assert diagnostics["schedule"]["last_update_success"]
    assert "private-marker" not in json.dumps(diagnostics)
    assert await hass.config_entries.async_unload(entry.entry_id)


async def test_json_decoder_resource_failure_is_an_explicit_schema_error(monkeypatch):
    def exhausted(*args, **kwargs):
        raise RecursionError

    client, _ = client_with(Response(body=b"[]"))
    monkeypatch.setattr(api.json, "loads", exhausted)
    with pytest.raises(ProviderError):
        await client.async_get_json(LIVE_FEED)
    assert client.diagnostics()[LIVE_FEED]["json_status"] == "invalid"
