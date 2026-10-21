"""Measure shared HTTP and Recorder budgets through scheduled real HA updates."""

import asyncio
import json
from datetime import timedelta
from unittest.mock import patch

import pytest
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.util import dt as dt_util
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from test_adaptive_polling import SyntheticProvider, setup_synthetic
from test_api import Response, client_with
from test_config_flow import user_input
from test_events import BASE
from test_init import demo_entry
from test_live_timing import timing_payload
from test_phase3a_sensors import entity_id

from custom_components.nascar_race_center import api
from custom_components.nascar_race_center.const import DOMAIN
from custom_components.nascar_race_center.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.nascar_race_center.endpoints import LIVE_FEED
from custom_components.nascar_race_center.models import parse_live
from custom_components.nascar_race_center.provider import DemoProvider


@pytest.mark.parametrize("kind", ["race", "practice", "qualifying"])
async def test_measured_http_budget_through_real_ha_scheduler(
    hass, freezer, monkeypatch, kind
):
    """Count actual fake-session GETs, rather than calling the decision function."""
    freezer.move_to(BASE)
    monkeypatch.setattr(
        api, "_monotonic", lambda: 1000 + (dt_util.utcnow() - BASE).total_seconds()
    )
    bodies = []
    for second in range(0, 601, 10):
        payload = timing_payload()
        payload.update(
            time_of_day_os=(BASE + timedelta(seconds=second)).isoformat(),
            run_type={"race": 3, "practice": 1, "qualifying": 2}[kind],
        )
        if kind != "race":
            payload.update(lap_number=0, flag_state=0)
            for row in payload["vehicles"]:
                row["is_on_track"] = True
                row.pop("laps_completed", None)
        bodies.append(Response(body=json.dumps(payload).encode()))
    client, session = client_with(*bodies)

    class TransportSynthetic(DemoProvider):
        api = client

        async def async_get_live(self):
            return parse_live(
                await client.async_get_json(
                    LIVE_FEED, minimum_ttl=10, minimum_interval=10
                )
            )

    entry = await setup_synthetic(
        hass,
        TransportSynthetic(),
        favorites=tuple(str(x) for x in range(99001, 99011)),
        events=False,
    )
    for _ in range(60):
        freezer.tick(10)
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
    assert session.get.call_count == 61
    assert entry.runtime_data.live.update_interval == timedelta(seconds=10)
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["live"]["polling"]["reason"] == f"active_{kind}"
    assert diagnostics["live"]["polling"]["source_content_age_seconds"] == 0
    assert client.diagnostics()[LIVE_FEED]["delivery"] == "network"
    assert (
        client.diagnostics()[LIVE_FEED]["successful_response_at"]
        == (BASE + timedelta(seconds=600)).isoformat()
    )
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.fixture
def mock_recorder_before_hass(request):
    if "recorder_mock" in request.fixturenames:
        request.getfixturevalue("recorder_db_url")


async def test_recorder_budget_at_scheduled_ten_second_cadence(
    recorder_mock, hass, freezer
):
    from homeassistant.components.recorder.db_schema import States, StatesMeta
    from pytest_homeassistant_custom_component.components.recorder.common import (
        async_wait_recording_done,
    )
    from sqlalchemy import func, select

    freezer.move_to(BASE)
    provider = SyntheticProvider()
    entry = await setup_synthetic(hass, provider, events=False)
    watched = tuple(
        entity_id(hass, entry, suffix)
        for suffix in ("driver_99001_live_position", "1_current_lap", "1_leader")
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
    before = await hass.async_add_executor_job(counts)
    assert all(before.get(key, 0) >= 1 for key in watched)
    for _ in range(10):
        freezer.tick(10)
        async_fire_time_changed(hass)
        await hass.async_block_till_done()
    await async_wait_recording_done(hass)
    assert await hass.async_add_executor_job(counts) == before
    provider.position = 8
    freezer.tick(10)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    await async_wait_recording_done(hass)
    after = await hass.async_add_executor_job(counts)
    assert after[watched[0]] == before[watched[0]] + 1
    assert after[watched[1]] == before[watched[1]]
    assert after[watched[2]] == before[watched[2]]
    assert len(provider.reads) == 12
    assert await hass.config_entries.async_unload(entry.entry_id)


@pytest.mark.parametrize("cancelled", [False, True])
async def test_fast_failed_setup_cleans_poll_and_schedule_listeners(
    hass, freezer, cancelled
):
    freezer.move_to(BASE)
    provider = SyntheticProvider()
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={"provider": "demo", "series": ["1"], "live_polling_policy": "adaptive"},
    )
    entry.add_to_hass(hass)
    with (
        patch(
            "custom_components.nascar_race_center.DemoProvider", return_value=provider
        ),
        patch.object(
            hass.config_entries,
            "async_forward_entry_setups",
            side_effect=asyncio.CancelledError()
            if cancelled
            else RuntimeError("Synthetic forwarding failure"),
        ),
    ):
        assert not await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    runtime = entry.runtime_data
    assert runtime.live._stopped
    assert not runtime.schedule._listeners
    assert not runtime.live._listeners
    freezer.tick(3600)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(provider.reads) == 1


@pytest.mark.parametrize(
    ("key", "value"),
    [
        ("live_polling_policy", "fast"),
        ("approaching_interval", 29),
        ("approaching_interval", 61),
        ("approaching_interval", True),
        ("approaching_interval", 30.5),
    ],
)
async def test_options_validation_and_legacy_defaults(hass, key, value):
    import probatio

    entry = MockConfigEntry(domain=DOMAIN, data=user_input(), unique_id=DOMAIN)
    entry.add_to_hass(hass)
    form = await hass.config_entries.options.async_init(entry.entry_id)
    if value == 30.5:
        result = await hass.config_entries.options.async_configure(
            form["flow_id"], user_input=user_input(**{key: value})
        )
        assert result["type"] is FlowResultType.FORM
        assert key in result["errors"]
    else:
        with pytest.raises(probatio.Invalid):
            form["data_schema"](user_input(**{key: value}))


async def test_legacy_entry_defaults_and_adaptive_options_reload_keep_ids(
    hass, freezer
):
    freezer.move_to(BASE)
    provider = SyntheticProvider()
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
        runtime = entry.runtime_data
        assert runtime.live.polling_policy == "conservative"
        assert runtime.live.update_interval == timedelta(seconds=300)
        saved = entity_id(hass, entry, "1_current_lap")
        form = await hass.config_entries.options.async_init(entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            form["flow_id"],
            user_input=user_input(
                live_polling_policy="adaptive", approaching_interval=45
            ),
        )
        assert result["type"] is FlowResultType.CREATE_ENTRY
        await hass.async_block_till_done()
        assert entry.runtime_data is not runtime
        assert runtime.live._stopped
        assert entry.runtime_data.live.update_interval == timedelta(seconds=10)
        assert entity_id(hass, entry, "1_current_lap") == saved
        assert entry.version == 1
        assert await hass.config_entries.async_unload(entry.entry_id)
