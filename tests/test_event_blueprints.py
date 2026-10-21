"""Validate and execute the shipped blueprints with actual HA automation/scenes."""

import asyncio
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from homeassistant.components.automation.config import AUTOMATION_BLUEPRINT_SCHEMA
from homeassistant.components.blueprint.models import Blueprint, BlueprintInputs
from homeassistant.components.demo.light import DemoLight
from homeassistant.components.light import DATA_COMPONENT
from homeassistant.exceptions import HomeAssistantError
from homeassistant.setup import async_setup_component
from homeassistant.util import dt as dt_util
from homeassistant.util import yaml as yaml_util
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.nascar_race_center.events import EVENT_NAMESPACE

ROOT = Path(__file__).parents[1] / "blueprints/automation/nascar_race_center"


def automation(name, inputs, alias):
    data = yaml_util.load_yaml(str(ROOT / name))
    blueprint = Blueprint(
        data, expected_domain="automation", schema=AUTOMATION_BLUEPRINT_SCHEMA
    )
    instance = BlueprintInputs(
        blueprint,
        {"use_blueprint": {"path": name, "input": inputs}, "alias": alias, "id": alias},
    )
    instance.validate()
    return instance.async_substitute()


def fire_flag(hass, flag="yellow", series=1, source="nascar_cf"):
    hass.bus.async_fire(
        EVENT_NAMESPACE,
        {
            "event_type": "flag_changed",
            "event_id": "synthetic-id",
            "series_id": series,
            "race_id": 9001,
            "run_id": 8,
            "driver_id": None,
            "flag": flag,
            "source": source,
            "source_time": dt_util.utcnow().isoformat(),
        },
    )


async def settle_effect():
    # HA tracks a running automation as an unfinished task. Drain ready callbacks
    # without waiting for its intentionally pending timeout/event trigger.
    for _ in range(60):
        await asyncio.sleep(0)


async def test_notification_blueprint_only_runs_user_selected_actions(hass):
    calls = []
    hass.services.async_register(
        "test_notification", "send", lambda call: calls.append(call.data)
    )
    config = automation(
        "race_notifications.yaml",
        {
            "notify_actions": [
                {
                    "action": "test_notification.send",
                    "data": {"message": "{{ racing_message }}"},
                }
            ]
        },
        "race_notifications",
    )
    assert await async_setup_component(hass, "automation", {"automation": [config]})
    await hass.async_block_till_done()
    fire_flag(hass, source="demo")
    fire_flag(hass, series=4)
    await hass.async_block_till_done()
    assert calls == []
    fire_flag(hass, flag="checkered")
    await hass.async_block_till_done()
    assert len(calls) == 1
    assert "flag changed" in calls[0]["message"]


@pytest.mark.parametrize("initially_on", [False, True])
async def test_flag_lights_restore_after_rapid_flags(hass, freezer, initially_on):
    assert await async_setup_component(hass, "light", {})
    assert await async_setup_component(hass, "scene", {})
    light = DemoLight(
        device_name="Race effect light",
        state=initially_on,
        hs_color=(220, 50),
        brightness=80,
        unique_id="race_effect",
    )
    await hass.data[DATA_COMPONENT].async_add_entities([light])
    await hass.async_block_till_done()
    entity_id = light.entity_id
    original = hass.states.get(entity_id)
    config = automation(
        "flag_lights.yaml", {"lights": [entity_id], "seconds": 3}, "flag_lights"
    )
    assert await async_setup_component(hass, "automation", {"automation": [config]})
    await hass.async_block_till_done()
    assert hass.states.get("automation.flag_lights") is not None
    fire_flag(hass, "yellow")
    await settle_effect()
    assert hass.states.get(entity_id).state == "on"
    assert hass.states.get(entity_id).attributes["hs_color"] != original.attributes.get(
        "hs_color"
    )
    fire_flag(hass, "red")
    await settle_effect()
    assert hass.states.get(entity_id).attributes["hs_color"] == (0, 100)
    fire_flag(hass, "green")
    await settle_effect()
    assert hass.states.get(entity_id).attributes["hs_color"] == (120, 100)
    # The latest effect expires, then restores on/off, brightness and color.

    future = dt_util.utcnow() + timedelta(seconds=4)
    freezer.move_to(future)
    async_fire_time_changed(hass, future)
    await settle_effect()
    restored = hass.states.get(entity_id)
    assert restored.state == original.state
    if initially_on:
        assert restored.attributes["brightness"] == original.attributes["brightness"]
        assert restored.attributes["hs_color"] == original.attributes["hs_color"]
    assert hass.states.async_entity_ids("scene") == []


async def test_color_command_failure_still_restores_light(hass, freezer):
    assert await async_setup_component(hass, "light", {})
    assert await async_setup_component(hass, "scene", {})
    light = DemoLight(
        device_name="Race effect light", state=False, unique_id="race_effect"
    )
    await hass.data[DATA_COMPONENT].async_add_entities([light])
    config = automation(
        "flag_lights.yaml", {"lights": [light.entity_id], "seconds": 1}, "flag_lights"
    )
    assert await async_setup_component(hass, "automation", {"automation": [config]})
    await hass.async_block_till_done()

    with patch.object(
        light,
        "async_turn_on",
        side_effect=HomeAssistantError("Synthetic unavailable device"),
    ):
        fire_flag(hass)
        await settle_effect()

        future = dt_util.utcnow() + timedelta(seconds=2)
        freezer.move_to(future)
        async_fire_time_changed(hass, future)
        await settle_effect()
    assert hass.states.get(light.entity_id).state == "off"
    assert hass.states.async_entity_ids("scene") == []


async def test_failed_restoration_retains_scene_and_blocks_future_effects(
    hass, freezer
):
    assert await async_setup_component(hass, "light", {})
    assert await async_setup_component(hass, "scene", {})
    light = DemoLight(
        device_name="Recovery light",
        state=True,
        hs_color=(220, 50),
        brightness=80,
        unique_id="recovery",
    )
    await hass.data[DATA_COMPONENT].async_add_entities([light])
    config = automation(
        "flag_lights.yaml", {"lights": [light.entity_id], "seconds": 1}, "recovery"
    )
    assert await async_setup_component(hass, "automation", {"automation": [config]})
    await hass.async_block_till_done()
    fire_flag(hass)
    await settle_effect()
    scene_id = "scene.nascar_flag_recovery"
    assert hass.states.get(scene_id) is not None
    with patch.object(
        light,
        "async_turn_on",
        side_effect=HomeAssistantError("Synthetic restoration failure"),
    ):
        future = dt_util.utcnow() + timedelta(seconds=2)
        freezer.move_to(future)
        async_fire_time_changed(hass, future)
        await settle_effect()
    assert hass.states.get(scene_id) is not None
    # An outstanding snapshot cannot be replaced with the failed effect state.
    with patch.object(light, "async_turn_on") as turn_on:
        fire_flag(hass, "red")
        await settle_effect()
        turn_on.assert_not_called()
    await hass.services.async_call(
        "scene", "turn_on", {"entity_id": scene_id}, blocking=True
    )
    await hass.async_block_till_done()
    restored = hass.states.get(light.entity_id)
    assert restored.attributes["hs_color"] == (220, 50)
    assert restored.attributes["brightness"] == 80
