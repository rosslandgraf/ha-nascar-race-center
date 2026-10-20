"""Lifecycle integration tests against the prepared Home Assistant runtime."""

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.nascar_race_center.const import (
    CONF_DATA_USE_AUTHORIZED,
    CONF_LIVE_INTERVAL,
    CONF_PROVIDER,
    CONF_SERIES,
    DOMAIN,
    PROVIDER_DEMO,
)


def demo_entry(series: list[str] | None = None) -> MockConfigEntry:
    """Create a credential-free entry with a stable single-instance unique ID."""
    return MockConfigEntry(
        domain=DOMAIN,
        unique_id=DOMAIN,
        title="NASCAR Race Center",
        data={
            CONF_PROVIDER: PROVIDER_DEMO,
            CONF_SERIES: series if series is not None else ["1", "2", "3"],
            CONF_DATA_USE_AUTHORIZED: False,
            CONF_LIVE_INTERVAL: 300,
        },
    )


async def test_demo_setup_and_clean_unload(hass: HomeAssistant) -> None:
    """Offline demo exposes all selected series and unloads their platforms."""
    entry = demo_entry()
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)
    entries = er.async_entries_for_config_entry(registry, entry.entry_id)
    assert entries
    for series in (1, 2, 3):
        assert registry.async_get_entity_id(
            "sensor", DOMAIN, f"{entry.entry_id}_{series}_next_race"
        )
    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
    assert all(
        (state := hass.states.get(entity.entity_id)) is None
        or state.state == STATE_UNAVAILABLE
        for entity in entries
    )


async def test_reload_preserves_entity_unique_ids(hass: HomeAssistant) -> None:
    """Reloads reuse existing entity registry entries instead of duplicating them."""
    entry = demo_entry(["2"])
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    registry = er.async_get(hass)
    before = {
        entity.unique_id: entity.entity_id
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
    }
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    after = {
        entity.unique_id: entity.entity_id
        for entity in er.async_entries_for_config_entry(registry, entry.entry_id)
    }
    assert before == after
    assert all(f"{entry.entry_id}_2_" in unique_id for unique_id in after)


async def test_options_reload_changes_selected_series(hass: HomeAssistant) -> None:
    """Changing UI options updates loaded series through the entry listener."""
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    hass.config_entries.async_update_entry(
        entry, options={**entry.data, CONF_SERIES: ["3"]}
    )
    await hass.async_block_till_done()
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_3_next_race"
    )
    assert entity_id is not None
    assert hass.states.get(entity_id) is not None
    cup_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_1_next_race"
    )
    assert cup_id is not None
    assert hass.states.get(cup_id).state == STATE_UNAVAILABLE


async def test_cf_cannot_bypass_authorization_during_setup(hass: HomeAssistant) -> None:
    """Even imported/corrupted entries cannot start CF collection without consent."""
    from unittest.mock import patch

    from custom_components.nascar_race_center.const import PROVIDER_CF

    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            CONF_PROVIDER: PROVIDER_CF,
            CONF_SERIES: ["1"],
            CONF_DATA_USE_AUTHORIZED: False,
        },
    )
    entry.add_to_hass(hass)
    with patch("custom_components.nascar_race_center.CFProvider") as provider:
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.SETUP_ERROR
    provider.assert_not_called()


async def test_malformed_saved_series_fails_cleanly(hass: HomeAssistant) -> None:
    """Invalid saved data produces a handled setup error before provider access."""
    from unittest.mock import patch

    entry = demo_entry(["invalid"])
    entry.add_to_hass(hass)
    with patch("custom_components.nascar_race_center.DemoProvider") as provider:
        assert not await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.SETUP_ERROR
    provider.assert_not_called()


async def test_optional_live_failure_during_setup_preserves_schedules(
    hass: HomeAssistant,
) -> None:
    """A live outage cannot prevent installing useful next-race entities."""
    from datetime import timedelta
    from unittest.mock import AsyncMock, Mock, patch

    from homeassistant.util import dt as dt_util

    from custom_components.nascar_race_center.api import ProviderError
    from custom_components.nascar_race_center.models import Race

    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        return_value=(
            Race(1, 10, "Future fixture race", dt_util.utcnow() + timedelta(days=1)),
        )
    )
    provider.async_get_live = AsyncMock(side_effect=ProviderError("Live feed down"))
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)
    next_race_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_1_next_race"
    )
    assert next_race_id is not None
    assert hass.states.get(next_race_id).state == "Future fixture race"
    status_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_1_feed_status"
    )
    assert status_id is not None
    assert hass.states.get(status_id).state == "offline"


async def test_initial_schedule_denial_loads_health_and_live_entities(
    hass: HomeAssistant,
) -> None:
    """First-boot metadata failure remains visible without rapid setup retries."""
    from datetime import timedelta
    from unittest.mock import AsyncMock, Mock, patch

    from homeassistant.util import dt as dt_util

    from custom_components.nascar_race_center.api import ProviderError
    from custom_components.nascar_race_center.diagnostics import (
        async_get_config_entry_diagnostics,
    )
    from custom_components.nascar_race_center.models import LiveSnapshot, Race

    provider = Mock()
    provider.async_get_schedule = AsyncMock(
        side_effect=ProviderError("Schedule denied", status=403)
    )
    provider.async_get_live = AsyncMock(
        return_value=LiveSnapshot(
            1, 10, flag="yellow", source_updated_at=dt_util.utcnow()
        )
    )
    entry = demo_entry(["1"])
    entry.add_to_hass(hass)
    with patch(
        "custom_components.nascar_race_center.DemoProvider", return_value=provider
    ):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.LOADED
    registry = er.async_get(hass)
    next_race_id = registry.async_get_entity_id(
        "sensor", DOMAIN, f"{entry.entry_id}_1_next_race"
    )
    flag_id = registry.async_get_entity_id("sensor", DOMAIN, f"{entry.entry_id}_1_flag")
    assert next_race_id is not None
    assert flag_id is not None
    assert hass.states.get(next_race_id).state == STATE_UNAVAILABLE
    assert hass.states.get(flag_id).state == "yellow"
    diagnostics = await async_get_config_entry_diagnostics(hass, entry)
    assert diagnostics["schedule"]["last_update_success"] is False
    assert diagnostics["schedule"]["last_http_status"] == 403
    provider.async_get_schedule.assert_awaited_once()

    provider.async_get_schedule.side_effect = None
    provider.async_get_schedule.return_value = (
        Race(1, 20, "Recovered schedule", dt_util.utcnow() + timedelta(days=1)),
    )
    await entry.runtime_data.schedule.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(next_race_id).state == "Recovered schedule"
