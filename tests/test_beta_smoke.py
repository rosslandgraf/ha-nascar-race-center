"""Owner-install journey on actual HA fixtures, with unmodified offline providers.

These are development-server checks, not physical HA OS/device acceptance.
Only loopback HTTP is permitted, including the authenticated native HA socket.
"""

import json
import time
from datetime import UTC, datetime
from unittest.mock import patch

import aiohttp
import pytest
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from test_config_flow import user_input
from test_dashboard_websocket import call, receive_update
from yarl import URL

from custom_components.nascar_race_center.const import CONF_FAVORITE_DRIVERS, DOMAIN
from custom_components.nascar_race_center.dashboard_snapshots import STORE_KEY
from custom_components.nascar_race_center.diagnostics import (
    async_get_config_entry_diagnostics,
)


@pytest.fixture
def loopback_only_http():
    """Fail before any external HTTP; leave real HA client/server traffic intact."""
    original = aiohttp.ClientSession._request
    external = []

    async def request(session, method, url, *args, **kwargs):
        if URL(url).host not in {"127.0.0.1", "localhost", "::1"}:
            external.append(URL(url).host)
            raise AssertionError("Offline beta attempted external HTTP")
        return await original(session, method, url, *args, **kwargs)

    with patch.object(aiohttp.ClientSession, "_request", request):
        yield external
    assert external == []


@pytest.mark.parametrize("series", [["1", "2", "3"], ["2"]])
async def test_beta_offline_install_options_recovery_and_removal(
    hass, hass_ws_client, hass_read_only_access_token, loopback_only_http, series
):
    """Exercise the real flow, calendars, API, options and unaffected HA service."""
    assert await async_setup_component(
        hass, "input_boolean", {"input_boolean": {"beta_existing": {}}}
    )
    assert await async_setup_component(
        hass,
        "automation",
        {
            "automation": [
                {
                    "alias": "Existing household test automation",
                    "triggers": [{"trigger": "event", "event_type": "beta_household"}],
                    "actions": [
                        {
                            "action": "input_boolean.turn_on",
                            "target": {"entity_id": "input_boolean.beta_existing"},
                        }
                    ],
                }
            ]
        },
    )
    started = time.perf_counter()
    flow = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    created = await hass.config_entries.flow.async_configure(
        flow["flow_id"],
        user_input=user_input(series=series, favorite_drivers=["99002"]),
    )
    assert created["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    setup_seconds = time.perf_counter() - started
    entry = created["result"]
    registry = er.async_get(hass)

    def identities():
        return {
            entity.unique_id: entity.entity_id
            for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
        }

    before = identities()
    assert before
    for selected in series:
        calendar_id = registry.async_get_entity_id(
            "calendar", DOMAIN, f"{entry.entry_id}_{selected}_calendar"
        )
        assert calendar_id is not None
        year = dt_util.utcnow().year
        events = await hass.services.async_call(
            "calendar",
            "get_events",
            {
                "entity_id": calendar_id,
                "start_date_time": datetime(year, 1, 1, tzinfo=UTC).isoformat(),
                "end_date_time": datetime(year + 1, 1, 1, tzinfo=UTC).isoformat(),
            },
            blocking=True,
            return_response=True,
        )
        assert events[calendar_id]["events"]
        assert all(
            "Demo" in event["summary"] for event in events[calendar_id]["events"]
        )

    client = await hass_ws_client(hass)
    bootstrap = (await call(client, entry, "bootstrap"))["result"]["data"]
    assert bootstrap["provider"] == "demo"
    assert bootstrap["series_ids"] == list(map(int, series))
    assert bootstrap["favorite_driver_ids"] == ["99002"]
    assert bootstrap["capabilities"]["access"] == "administrator"
    selected = int(series[0])
    schedule = (await call(client, entry, "schedule", series_id=selected))["result"][
        "data"
    ]
    assert {row["kind"] for row in schedule["records"]} == {"race", "session"}
    await call(client, entry, "subscribe_live", series_id=selected)
    live = await receive_update(client)
    assert live["availability"] == "no_active_session"
    assert live["leaderboard"] is None

    restricted = await hass_ws_client(hass, access_token=hass_read_only_access_token)
    assert (await call(restricted, entry, "bootstrap"))["error"][
        "code"
    ] == "unauthorized"
    await restricted.close()

    key = {"series_id": selected, "season": year, "race_id": year * 100 + selected}
    history = (
        await call(
            client, entry, "history", **key, datasets=["weekend", "laps"], limit=1
        )
    )["result"]["data"]
    assert history["pagination"]["next_offset"] is not None
    next_page = await call(
        client,
        entry,
        "history",
        **key,
        datasets=["weekend", "laps"],
        limit=200,
        offset=history["pagination"]["next_offset"],
        snapshot=history["pagination"]["snapshot"],
    )
    assert next_page["success"]
    assert any(
        row["kind"] == "result" for row in next_page["result"]["data"]["records"]
    )
    analytics = await call(
        client,
        entry,
        "analytics",
        **key,
        datasets=["weekend", "laps"],
        driver_ids=[99002],
        first_lap=1,
        last_lap=10,
        windows=[5],
        time_basis="all_available",
    )
    assert analytics["success"]
    assert not any(
        row["kind"] == "samples" for row in analytics["result"]["data"]["records"]
    )
    assert len(hass.data[STORE_KEY].leases) == 2
    await client.close()
    await hass.async_block_till_done()
    assert not hass.data[STORE_KEY].leases
    assert not entry.runtime_data.dashboard.subscriptions

    reconnected = await hass_ws_client(hass)
    assert (
        await call(
            reconnected,
            entry,
            "history",
            **key,
            datasets=["weekend", "laps"],
            offset=1,
            snapshot=history["pagination"]["snapshot"],
        )
    )["error"]["code"] == "snapshot_invalid"
    await reconnected.close()
    options = await hass.config_entries.options.async_init(entry.entry_id)
    await hass.config_entries.options.async_configure(
        options["flow_id"],
        user_input=user_input(series=series, favorite_drivers=["99001", "99002"]),
    )
    await hass.async_block_till_done()
    assert all(identities()[uid] == entity_id for uid, entity_id in before.items())
    assert entry.options[CONF_FAVORITE_DRIVERS] == ["99001", "99002"]
    after_options = identities()
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert identities() == after_options
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["provider"] == "demo"
    assert diagnostics["events"]["status"] == "disabled"
    assert diagnostics["reference"]["favorite_count"] == 2
    assert "http://" not in json.dumps(diagnostics)
    assert await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.config_entries.async_get_entry(entry.entry_id) is None
    assert not er.async_entries_for_config_entry(registry, entry.entry_id)
    hass.bus.async_fire("beta_household")
    await hass.async_block_till_done()
    assert hass.states.get("input_boolean.beta_existing").state == "on"
    print(f"BETA_DEVELOPMENT_SETUP_SECONDS series={series}: {setup_seconds:.6f}")
